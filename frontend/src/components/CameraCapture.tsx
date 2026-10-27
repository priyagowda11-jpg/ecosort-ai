import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";

export function CameraCapture({ onPhoto, onClose }: { onPhoto: (f: File) => void; onClose: () => void }) {
  const { t } = useI18n();
  const video = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [shot, setShot] = useState<{ file: File; url: string } | null>(null);

  const stop = () => { stream.current?.getTracks().forEach(tr => tr.stop()); stream.current = null; };
  const start = async () => {
    if (!navigator.mediaDevices?.getUserMedia) return setErr("cam.unsupported");
    try {   // permission is requested here, only after the user chose camera mode
      stream.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      if (video.current) video.current.srcObject = stream.current;
    } catch (e) {
      const n = (e as DOMException).name;
      setErr(n === "NotAllowedError" || n === "SecurityError" ? "cam.denied" : n === "NotFoundError" ? "cam.none" : "cam.error");
    }
  };
  useEffect(() => { start(); return stop; }, []);       // tracks stop on unmount
  useEffect(() => () => { if (shot) URL.revokeObjectURL(shot.url); }, [shot]);

  const capture = () => {
    const v = video.current; if (!v || !v.videoWidth) return;
    const c = document.createElement("canvas"); c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext("2d")!.drawImage(v, 0, 0);
    c.toBlob(b => { if (b) { const file = new File([b], "capture.jpg", { type: "image/jpeg" }); setShot({ file, url: URL.createObjectURL(b) }); } }, "image/jpeg", 0.92);
  };
  const close = () => { stop(); onClose(); };

  if (err) return <div role="alert" className="notice error">{t(err)} <button className="btn" onClick={close}>{t("cam.close")}</button></div>;
  return (
    <div className="camera">
      {shot ? <img src={shot.url} alt="" /> : <video ref={video} autoPlay playsInline muted aria-label="Camera preview" />}
      <div className="row">
        {shot ? (<>
          <button className="btn" onClick={() => setShot(null)}>{t("cam.retake")}</button>
          <button className="btn primary" onClick={() => { stop(); onPhoto(shot.file); }}>{t("cam.use")}</button>
        </>) : <button className="btn primary" onClick={capture}>{t("cam.capture")}</button>}
        <button className="btn" onClick={close}>{t("cam.close")}</button>
      </div>
    </div>
  );
}
