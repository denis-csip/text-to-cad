"""
Envoi LAN vers une imprimante Bambu (X1C) -- maillon 3 du proto text-to-CAD.

Protocole LAN Bambu :
  1) Upload du 3mf tranche via FTPS implicite (port 990, user 'bblp', pass = access code)
  2) Lecture d'etat + demarrage via MQTT/TLS (port 8883, meme identifiants)

SECURITE : dry-run par defaut. Le script se connecte, lit l'etat et televerse le
fichier (inoffensif), puis AFFICHE la commande de demarrage SANS l'envoyer.
Il ne lance reellement l'impression qu'avec le flag --start (a faire devant la machine).

Usage :
  python bambu_lan_send.py --ip 192.168.x.x --code 12345678 --serial 01P00A... \
      --file out/cable_clip_orca.3mf            # DRY-RUN (defaut)
  python bambu_lan_send.py ... --start          # DEMARRE l'impression
"""
import argparse, ftplib, ssl, socket, json, sys, time, os


# ---- FTPS implicite (Bambu ecoute en TLS des la connexion, port 990) ----
class ImplicitFTP_TLS(ftplib.FTP_TLS):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._sock = None

    @property
    def sock(self):
        return self._sock

    @sock.setter
    def sock(self, value):
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value, server_hostname=None)
        self._sock = value


def ftps_upload(ip, code, local_path, remote_name):
    ctx = ssl._create_unverified_context()
    ftp = ImplicitFTP_TLS(context=ctx)
    ftp.connect(host=ip, port=990, timeout=20)
    ftp.login("bblp", code)
    ftp.prot_p()
    size = os.path.getsize(local_path)
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_name}", f)
    try:
        listing = []
        ftp.retrlines("LIST", listing.append)
    except Exception:
        listing = ["(LIST indisponible)"]
    ftp.quit()
    return size, listing


# ---- MQTT : lecture d'etat + (option) demarrage ----
def mqtt_status_and_maybe_start(ip, code, serial, remote_name, subtask,
                                do_start, plate_gcode):
    import paho.mqtt.client as mqtt

    state = {"connected": False, "report": None}
    req_topic = f"device/{serial}/request"
    rep_topic = f"device/{serial}/report"

    def on_connect(c, u, flags, rc, props=None):
        state["connected"] = (rc == 0)
        c.subscribe(rep_topic)
        c.publish(req_topic, json.dumps({"pushing": {
            "sequence_id": "0", "command": "pushall"}}))

    def on_message(c, u, msg):
        try:
            state["report"] = json.loads(msg.payload.decode())
        except Exception:
            pass

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.username_pw_set("bblp", code)
    c.tls_set(cert_reqs=ssl.CERT_NONE)
    c.tls_insecure_set(True)
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(ip, 8883, 60)
    c.loop_start()

    t0 = time.time()
    while time.time() - t0 < 6 and state["report"] is None:
        time.sleep(0.2)

    # Commande de demarrage d'un projet 3mf deja televersE (SD card)
    start_payload = {"print": {
        "sequence_id": "0",
        "command": "project_file",
        "param": plate_gcode,                 # ex: Metadata/plate_1.gcode
        "url": f"file:///sdcard/{remote_name}",
        "subtask_name": subtask,
        "task_id": "0", "subtask_id": "0", "project_id": "0", "profile_id": "0",
        "use_ams": False, "ams_mapping": [],
        "timelapse": False, "bed_leveling": True,
        "flow_cali": False, "vibration_cali": True, "layer_inspect": True,
    }}

    result = {"state": state, "start_payload": start_payload, "started": False}
    if do_start:
        c.publish(req_topic, json.dumps(start_payload))
        time.sleep(1.0)
        result["started"] = True
    c.loop_stop()
    c.disconnect()
    return result


def summarize_report(rep):
    if not rep:
        return "  (pas de rapport recu -- imprimante joignable mais silencieuse)"
    p = rep.get("print", rep)
    keys = ["gcode_state", "nozzle_temper", "bed_temper", "mc_percent",
            "mc_remaining_time", "print_error", "wifi_signal"]
    lines = []
    for k in keys:
        if k in p:
            lines.append(f"  {k:18s}: {p[k]}")
    return "\n".join(lines) or "  (rapport recu, champs standard absents)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", required=True)
    ap.add_argument("--code", required=True, help="LAN access code (ecran imprimante)")
    ap.add_argument("--serial", required=True)
    ap.add_argument("--file", required=True, help="chemin du 3mf tranche")
    ap.add_argument("--name", default=None, help="nom distant (defaut: basename)")
    ap.add_argument("--plate-gcode", default="Metadata/plate_1.gcode")
    ap.add_argument("--start", action="store_true",
                    help="DEMARRE reellement l'impression (sinon dry-run)")
    a = ap.parse_args()

    remote = a.name or os.path.basename(a.file)
    subtask = os.path.splitext(remote)[0]
    mode = "DEMARRAGE REEL" if a.start else "DRY-RUN (aucun demarrage)"
    print(f"=== Bambu LAN send -- {mode} ===")
    print(f"  cible   : {a.ip}  (serial {a.serial})")
    print(f"  fichier : {a.file}  ->  /{remote}")

    print("\n[1/3] Connexion MQTT + lecture d'etat...")
    try:
        res = mqtt_status_and_maybe_start(
            a.ip, a.code, a.serial, remote, subtask,
            do_start=False, plate_gcode=a.plate_gcode)  # jamais de start ici
        print("  connecte." if res["state"]["connected"] else "  echec auth MQTT.")
        print(summarize_report(res["state"]["report"]))
    except Exception as e:
        print(f"  [ERREUR MQTT] {e}")
        print("  -> verifie IP / access code / que tu es sur le meme reseau.")
        sys.exit(2)

    print("\n[2/3] Upload FTPS du 3mf...")
    try:
        size, listing = ftps_upload(a.ip, a.code, a.file, remote)
        print(f"  televerse : {size} octets.")
    except Exception as e:
        print(f"  [ERREUR FTPS] {e}")
        sys.exit(3)

    print("\n[3/3] Commande de demarrage :")
    start = mqtt_status_and_maybe_start(
        a.ip, a.code, a.serial, remote, subtask,
        do_start=a.start, plate_gcode=a.plate_gcode)
    print(json.dumps(start["start_payload"]["print"], indent=2, ensure_ascii=False))
    if a.start:
        print("\n>>> DEMARRAGE ENVOYE. Surveille la machine.")
    else:
        print("\n--- DRY-RUN : commande NON envoyee. Relance avec --start pour imprimer. ---")


if __name__ == "__main__":
    main()
