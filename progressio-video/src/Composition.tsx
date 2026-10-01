import { Composition, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const scenes = [
  { eyebrow: "PROGRESSIO", title: ["Kenali dirimu.", "Tentukan arahmu."], body: "Ubah target keahlian menjadi perjalanan yang terukur.", tag: "PROGRESS → PROOF" },
  { eyebrow: "01 / TENTUKAN TUJUAN", title: ["Mulai dari", "targetmu."], body: "Pilih keahlian yang ingin kamu capai—misalnya Web Development.", tag: "TARGET · WEB DEVELOPMENT" },
  { eyebrow: "02 / UKUR KEMAMPUAN", title: ["Lihat posisi", "awalmu."], body: "Diagnostic memetakan kemampuan yang sudah kuat dan yang perlu diasah.", tag: "DIAGNOSTIC · 6 KOMPETENSI" },
  { eyebrow: "03 / TEMPUH ROADMAP", title: ["Langkah jelas.", "Arah personal."], body: "Ikuti path belajar dari skill gap-mu, dengan materi dari sumber terbuka.", tag: "ROADMAP · BERDASARKAN SKILL GAP" },
  { eyebrow: "04 / TUNJUKKAN BUKTI", title: ["Bukan sekadar", "sudah belajar."], body: "Assessment menilai bukti kemampuan terhadap standar kompetensi.", tag: "ASSESSMENT · EVIDENCE-BASED" },
  { eyebrow: "05 / HASIL DEMO", title: ["Progress yang", "bisa dibuktikan."], body: "Credential pada demo ini masih simulasi—belum terverifikasi.", tag: "CREDENTIAL · SIMULASI DEMO" },
];

const lime = "#b5f942";
const muted = "#abb5ab";
const cardStyle: React.CSSProperties = {
  background: "#20251f", border: "1px solid #414c3c", borderRadius: 18,
  padding: "22px 26px", color: "#f6f8f3", boxShadow: "0 16px 45px #0005",
};

const ProgressioVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sceneIndex = Math.min(Math.floor(frame / (5 * fps)), scenes.length - 1);
  const sceneFrame = frame - sceneIndex * 5 * fps;
  const scene = scenes[sceneIndex];
  const enter = spring({ frame: sceneFrame, fps, config: { damping: 18, stiffness: 110 } });
  const opacity = interpolate(sceneFrame, [0, 12, 132, 150], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shift = interpolate(enter, [0, 1], [28, 0]);
  const progress = (frame % (5 * fps)) / (5 * fps);

  return (
    <div style={{ width: "100%", height: "100%", background: "#14161d", color: "#f7faf4", fontFamily: "Arial, sans-serif", padding: "48px 72px", boxSizing: "border-box", position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, opacity: 0.12, backgroundImage: "radial-gradient(#b5f942 1px, transparent 1px)", backgroundSize: "28px 28px" }} />
      <div style={{ position: "absolute", width: 560, height: 560, borderRadius: "50%", background: "#b5f942", filter: "blur(180px)", opacity: 0.08, right: -160, top: 30 }} />
      <header style={{ position: "relative", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 25, fontWeight: 750, letterSpacing: -1 }}>progressio<span style={{ color: lime }}>.</span></div>
        <div style={{ fontSize: 13, color: muted, letterSpacing: 2 }}>TURNING PROGRESS INTO PROOF</div>
      </header>

      <main style={{ position: "relative", display: "grid", gridTemplateColumns: "1.15fr 0.85fr", gap: 56, alignItems: "center", height: 500, opacity, transform: `translateY(${shift}px)` }}>
        <section>
          <div style={{ color: lime, fontWeight: 700, fontSize: 14, letterSpacing: 2.5, marginBottom: 22 }}>{scene.eyebrow}</div>
          <h1 style={{ fontSize: 64, lineHeight: 1.04, letterSpacing: -2.6, margin: "0 0 24px", fontWeight: 750 }}>{scene.title.map((line) => <span key={line} style={{ display: "block" }}>{line}</span>)}</h1>
          <p style={{ color: muted, fontSize: 21, lineHeight: 1.5, maxWidth: 570, margin: "0 0 30px" }}>{scene.body}</p>
          <div style={{ display: "inline-block", border: "1px solid #4a5b3c", borderRadius: 999, padding: "10px 16px", color: lime, fontSize: 12, fontWeight: 700, letterSpacing: 1.2 }}>{scene.tag}</div>
        </section>

        <section style={{ position: "relative", minHeight: 300, display: "flex", justifyContent: "center", alignItems: "center" }}>
          {sceneIndex < 2 && <div style={{ ...cardStyle, width: 320, transform: `rotate(-3deg) scale(${0.96 + enter * 0.04})` }}>
            <div style={{ color: muted, fontSize: 12, letterSpacing: 1.5, marginBottom: 14 }}>{sceneIndex === 0 ? "YOUR NEXT CHAPTER" : "PILIH TARGET KEAHLIAN"}</div>
            <div style={{ fontSize: 24, fontWeight: 700, marginBottom: 20 }}>{sceneIndex === 0 ? "Satu langkah maju." : "Web Development"}</div>
            <div style={{ height: 8, background: "#394235", borderRadius: 8 }}><div style={{ width: `${35 + progress * 25}%`, height: "100%", background: lime, borderRadius: 8 }} /></div>
            <div style={{ display: "flex", justifyContent: "space-between", color: muted, fontSize: 12, marginTop: 12 }}><span>Perjalananmu</span><span>Dimulai dari sini ↗</span></div>
          </div>}
          {sceneIndex === 2 && <div style={{ ...cardStyle, width: 330 }}>
            <div style={{ fontSize: 12, color: muted, marginBottom: 18 }}>PETA KOMPETENSI</div>
            {["HTML & CSS", "JavaScript", "React", "API & Data"].map((item, i) => <div key={item} style={{ marginBottom: 16 }}><div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, marginBottom: 7 }}><span>{item}</span><span style={{ color: lime }}>{[82, 54, 36, 24][i]}%</span></div><div style={{ height: 6, background: "#394235", borderRadius: 8 }}><div style={{ height: "100%", width: `${[82, 54, 36, 24][i]}%`, background: i < 2 ? lime : "#7d916b", borderRadius: 8 }} /></div></div>)}
          </div>}
          {sceneIndex === 3 && <div style={{ display: "grid", gap: 12, width: 340 }}>{["Pondasi web", "JavaScript", "Bangun project"].map((x, i) => <div key={x} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: 16, transform: `translateX(${(1 - enter) * 45}px)` }}><div style={{ width: 30, height: 30, borderRadius: 50, display: "grid", placeItems: "center", background: i === 0 ? lime : "#394235", color: "#14161d", fontWeight: 700 }}>{i + 1}</div><div><div style={{ fontWeight: 700 }}>{x}</div><div style={{ color: muted, fontSize: 12, marginTop: 4 }}>{i === 0 ? "Materi · Open source" : i === 1 ? "Skill gap prioritas" : "Bukti lewat praktik"}</div></div></div>)}</div>}
          {sceneIndex === 4 && <div style={{ ...cardStyle, width: 330, transform: "rotate(2deg)" }}><div style={{ color: lime, fontSize: 12, letterSpacing: 1.5 }}>ASSESSMENT SUBMISSION</div><div style={{ fontSize: 22, fontWeight: 700, margin: "16px 0" }}>Portfolio project</div><div style={{ color: muted, fontSize: 14, lineHeight: 1.6 }}>Evidence dinilai terhadap kriteria kompetensi—bukan hanya durasi belajar.</div><div style={{ borderTop: "1px solid #414c3c", marginTop: 18, paddingTop: 16, display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>Status penilaian</span><span style={{ color: lime }}>Mock evaluator</span></div></div>}
          {sceneIndex === 5 && <div style={{ ...cardStyle, width: 330, borderColor: "#78964f", transform: `rotate(-2deg) scale(${0.96 + enter * 0.04})` }}><div style={{ display: "flex", justifyContent: "space-between", color: lime, fontSize: 12, letterSpacing: 1 }}>PROGRESSIO <span>DEMO</span></div><div style={{ height: 1, background: "#414c3c", margin: "20px 0" }} /><div style={{ color: muted, fontSize: 12 }}>CERTIFICATE OF ACHIEVEMENT</div><div style={{ fontSize: 24, fontWeight: 700, margin: "8px 0 18px" }}>Web Development</div><div style={{ border: "1px solid #a17a35", background: "#332c1d", color: "#f1c66b", borderRadius: 6, display: "inline-block", padding: "8px 10px", fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>SIMULASI · BELUM TERVERIFIKASI</div><div style={{ color: muted, fontSize: 12, marginTop: 18 }}>Preview credential untuk demo produk</div></div>}
        </section>
      </main>

      <footer style={{ position: "absolute", left: 72, right: 72, bottom: 38, display: "flex", justifyContent: "space-between", alignItems: "center", color: muted, fontSize: 12 }}>
        <div style={{ display: "flex", gap: 7 }}>{scenes.map((_, i) => <div key={i} style={{ height: 4, width: i === sceneIndex ? 38 : 14, borderRadius: 4, background: i <= sceneIndex ? lime : "#485045" }} />)}</div>
        <span>{sceneIndex === 5 ? "Ukur kemampuan. Tunjukkan buktinya." : `0${sceneIndex + 1}  /  06`}</span>
      </footer>
      <div style={{ position: "absolute", bottom: 0, left: 0, height: 3, width: `${(frame / (30 * fps)) * 100}%`, background: lime }} />
    </div>
  );
};

export const MyComposition = () => <Composition id="ProgressioIntro" component={ProgressioVideo} durationInFrames={30 * 30} fps={30} width={1280} height={720} />;
