import React, { useState, useEffect } from 'react';
import { Download, MonitorPlay, Trophy, Zap, Heart, Star, Box, Code2, Globe, Send, AlertTriangle } from 'lucide-react';
import appScreenshot from './assets/app_screenshot.png';


const GithubIcon = ({ size, color }) => (
  <svg width={size || 24} height={size || 24} color={color} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.2c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
    <path d="M9 18c-4.51 2-5-2-7-2"></path>
  </svg>
);

const Navbar = () => {
  return (
    <nav style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 100 }} className="glass-panel">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <MonitorPlay size={28} color="var(--accent)" />
        <h1 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, letterSpacing: '1px' }}>CHVSTX NEXUS</h1>
      </div>
      <div style={{ display: 'flex', gap: '20px' }}>
        <a href="#features" style={{ color: 'var(--text-bright)', fontWeight: 600 }}>Características</a>
        <a href="#changelog" style={{ color: 'var(--text-bright)', fontWeight: 600 }}>Novedades</a>
        <a href="#donate" style={{ color: 'var(--text-bright)', fontWeight: 600 }}>Apoyo</a>
        <a href="#contact" style={{ color: 'var(--text-bright)', fontWeight: 600 }}>Contacto</a>
        <a href="#disclaimer" style={{ color: 'var(--text-bright)', fontWeight: 600 }}>Legal</a>
        <a href="https://github.com/DavidFR-2000/ChvstxNexus" target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600 }}>
          <GithubIcon size={18} /> GitHub
        </a>
      </div>
    </nav>
  );
};

const Hero = () => {
  return (
    <section style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '40px' }} className="animate-fade-in-up">
      <div style={{ maxWidth: '800px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        <h1 style={{ fontSize: '4rem', fontWeight: 900, margin: 0, lineHeight: 1.1 }}>
          Tu Centro Definitivo de <br /><span className="gradient-text">Emulación Retro</span>
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-dim)', maxWidth: '600px', margin: '10px 0 30px' }}>
          La plataforma todo-en-uno definitiva para gestionar tus juegos, descargar portadas, conseguir logros y revivir las mejores joyas de la historia de los videojuegos.
        </p>
        
        <div style={{ display: 'flex', gap: '20px' }}>
          <a href="https://github.com/DavidFR-2000/ChvstxNexus/releases/latest" style={{ background: 'var(--accent)', color: 'var(--bg-dark)', padding: '15px 30px', borderRadius: '30px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.1rem', boxShadow: '0 4px 15px rgba(88, 166, 255, 0.4)' }}>
            <Download size={22} /> Descargar v4.0.2
          </a>
          <a href="#features" style={{ background: 'rgba(255, 255, 255, 0.1)', color: 'var(--text-bright)', padding: '15px 30px', borderRadius: '30px', fontWeight: 'bold', display: 'flex', alignItems: 'center', fontSize: '1.1rem', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            Descubrir Más
          </a>
        </div>
      </div>
      
      {/* App Screenshot */}
      <div className="glass-panel animate-float" style={{ marginTop: '60px', width: '90%', maxWidth: '1000px', borderRadius: '15px', border: '2px solid rgba(88,166,255,0.3)', overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#000', boxShadow: '0 20px 50px rgba(0,0,0,0.5)' }}>
        <img src={appScreenshot} alt="Chvstx Nexus App UI Screenshot" style={{ width: '100%', height: 'auto', display: 'block' }} />
      </div>
    </section>
  );
};

const Features = () => {
  const feats = [
    { icon: <Globe size={40} color="var(--accent)" />, title: "Hub In-App Integrado", desc: "Descarga, auto-extrae y configura tus emuladores y ROMs sin salir de la interfaz. 100% automático y blindado contra vulnerabilidades." },
    { icon: <Trophy size={40} color="#facc15" />, title: "RetroAchievements", desc: "Tus cuentas conectadas. Desbloquea trofeos clásicos, visualiza tus insignias y compara tus estadísticas en tiempo real." },
    { icon: <Zap size={40} color="#ff5e5e" />, title: "Ultrarrápido y Robusto", desc: "Motor central optimizado para evitar cuelgues (crashes). Logging detallado incorporado para una experiencia infalible." },
    { icon: <Box size={40} color="#a371f7" />, title: "Soporte Multi-Consola", desc: "Desde NES hasta consolas de 64 bits. Escaneo automático de carpetas, descargas de carátulas nativas e interfaces dinámicas." }
  ];

  return (
    <section id="features" style={{ padding: '80px 40px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '2.5rem', textAlign: 'center', marginBottom: '50px' }}>Por qué elegir <span className="gradient-text">Nexus</span></h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '30px' }}>
        {feats.map((f, i) => (
          <div key={i} className="glass-panel" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '15px', transition: 'transform 0.3s' }} 
               onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
               onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
            {f.icon}
            <h3 style={{ margin: '10px 0 0', fontSize: '1.2rem' }}>{f.title}</h3>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.95rem' }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

const Changelog = () => {
  const [release, setRelease] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://api.github.com/repos/DavidFR-2000/ChvstxNexus/releases/latest')
      .then(res => res.json())
      .then(data => { setRelease(data); setLoading(false); })
      .catch((e) => { console.error("Error Github API:", e); setLoading(false); });
  }, []);

  return (
    <section id="changelog" style={{ padding: '80px 40px', background: 'rgba(255,255,255,0.02)' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2.5rem', textAlign: 'center', marginBottom: '10px' }}><Code2 style={{display: 'inline', verticalAlign: 'middle', marginRight: '10px'}}/>Últimas Novedades</h2>
        <p style={{ color: 'var(--text-dim)', textAlign: 'center', marginBottom: '40px' }}>El código que alimenta tu nostalgia se actualiza constantemente.</p>
        
        <div className="glass-panel" style={{ padding: '40px' }}>
          {loading ? (
            <p style={{ textAlign:'center', color:'var(--text-dim)'}}>Refrescando desde GitHub...</p>
          ) : release && release.name ? (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', paddingBottom: '20px', marginBottom: '20px' }}>
                <h3 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--accent)' }}>{release.name}</h3>
                <span style={{ background: 'var(--bg-hover)', padding: '5px 12px', borderRadius: '15px', fontSize: '0.9rem' }}>{new Date(release.published_at).toLocaleDateString()}</span>
              </div>
              <div style={{ color: 'var(--text-dim)', whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.95rem' }}>
                {release.body || "Mantenimiento interno y correcciones menores sin log especificado."}
              </div>
              <a href={release.html_url} target="_blank" rel="noreferrer" style={{ display: 'inline-block', marginTop: '30px', padding: '10px 20px', background: 'var(--bg-hover)', borderRadius: '6px', border: '1px solid var(--border)'}}>
                Ver Release en GitHub
              </a>
            </>
          ) : (
            <p>No se pudo contactar con GitHub en este momento.</p>
          )}
        </div>
      </div>
    </section>
  );
};

const Community = () => {
  const reviews = [
    { author: "RetroGamer99", rating: 5, text: "Por fin una aplicación de emulación donde tenerlo todo ordenado es cosa de niños. Los logros in-app son perfectos." },
    { author: "PlayerOne", rating: 5, text: "Increíble que desde el Hub puedas bajar y extraer los cores de RetroArch solos. Cero complicaciones." },
    { author: "BitsNBytes", rating: 5, text: "La interfaz es limpia, sin lag, y me reconoce las roms a la primera. Excelente trabajo de desarrollo y mantenimiento." }
  ];

  return (
    <section style={{ padding: '80px 40px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '2.5rem', textAlign: 'center', marginBottom: '50px' }}>Voces de la Comunidad</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
        {reviews.map((r, i) => (
          <div key={i} className="glass-panel" style={{ padding: '30px', position: 'relative' }}>
            <div style={{ color: '#facc15', marginBottom: '15px', display: 'flex', gap: '5px' }}>
               {[...Array(r.rating)].map((_,j) => <Star key={j} size={18} fill="currentColor" />)}
            </div>
            <p style={{ fontStyle: 'italic', color: 'var(--text-dim)', marginBottom: '20px' }}>"{r.text}"</p>
            <p style={{ fontWeight: 'bold', margin: 0 }}>@{r.author}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

const Donate = () => {
  return (
    <section id="donate" style={{ padding: '80px 40px', background: 'radial-gradient(circle at center, rgba(88,166,255,0.1) 0%, rgba(18,18,18,1) 70%)', textAlign: 'center' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <Heart size={50} color="var(--accent2)" fill="var(--accent2)" style={{ marginBottom: '20px' }} />
        <h2 style={{ fontSize: '2.5rem', margin: '0 0 20px 0' }}>Apoya el Proyecto</h2>
        <p style={{ color: 'var(--text-dim)', fontSize: '1.1rem', marginBottom: '40px' }}>
          Chvstx Nexus es y seguirá siendo un software libre para la comunidad retro. 
          Tu apoyo ayuda a mantener las infraestructuras vivas y asegura horas de nuevo desarrollo.
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
           <a href="https://ko-fi.com/chvstx" target="_blank" rel="noreferrer" style={{ display: 'inline-block', padding: '15px 30px', background: '#FF5E5B', color: 'white', borderRadius: '30px', fontSize: '1.1rem', fontWeight: 'bold', textDecoration: 'none', transition: 'transform 0.2s', boxShadow: '0 4px 15px rgba(255, 94, 91, 0.4)' }} onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'} onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}>☕ Apoyar en Ko-Fi</a>
        </div>
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer style={{ padding: '40px', borderTop: '1px solid var(--border)', textAlign: 'center', color: 'var(--text-dim)' }}>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center', gap: '20px' }}>
        <a href="https://github.com/DavidFR-2000/ChvstxNexus" style={{ color: 'var(--text-dim)' }}><GithubIcon /></a>
      </div>
      <p style={{ margin: 0 }}>© {new Date().getFullYear()} Chvstx Nexus. Desarrollado con dedicación para los jugadores.</p>
    </footer>
  );
};

const Contact = () => {
  return (
    <section id="contact" style={{ padding: '80px 40px', maxWidth: '800px', margin: '0 auto' }}>
      <div className="glass-panel" style={{ padding: '40px', borderRadius: '20px' }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <Send size={40} color="var(--accent)" style={{ margin: '0 auto 15px auto', display: 'block' }} />
          <h2 style={{ fontSize: '2.5rem', margin: '0 0 10px 0' }}>Buzón de Sugerencias</h2>
          <p style={{ color: 'var(--text-dim)' }}>¿Has encontrado un bug o tienes una idea brutal para mejorar Chvstx Nexus? Escríbeme y me llegará directo al correo.</p>
        </div>
        
        {/* Formulario conectado a Formspree */}
        <form action="https://formspree.io/f/xdayagpo" method="POST" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: 'var(--text-bright)' }}>Tu nombre (opcional)</label>
            <input type="text" name="name" style={{ width: '100%', padding: '15px', borderRadius: '10px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', color: 'white', fontSize: '1rem', boxSizing: 'border-box' }} placeholder="Ej. RetroGamer99" />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: 'var(--text-bright)' }}>Correo para responderte (opcional)</label>
            <input type="email" name="email" style={{ width: '100%', padding: '15px', borderRadius: '10px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', color: 'white', fontSize: '1rem', boxSizing: 'border-box' }} placeholder="tu@correo.com" />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: 'var(--text-bright)' }}>Mensaje / Bug <span style={{ color: '#ff5e5e' }}>*</span></label>
            <textarea name="message" required rows="5" style={{ width: '100%', padding: '15px', borderRadius: '10px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', color: 'white', fontSize: '1rem', resize: 'vertical', boxSizing: 'border-box' }} placeholder="Describe detalladamente el problema o tu sugerencia..."></textarea>
          </div>
          <button type="submit" style={{ padding: '15px', background: 'var(--accent)', color: 'var(--bg-dark)', borderRadius: '10px', fontSize: '1.1rem', fontWeight: 'bold', border: 'none', cursor: 'pointer', marginTop: '10px' }}>
            Enviar Mensaje
          </button>
        </form>
      </div>
    </section>
  );
};

const Disclaimer = () => {
  return (
    <section id="disclaimer" style={{ padding: '40px', maxWidth: '1000px', margin: '40px auto', background: 'rgba(255,0,0,0.05)', borderRadius: '15px', border: '1px solid rgba(255,0,0,0.2)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px', color: '#ff5e5e' }}>
        <AlertTriangle size={30} />
        <h2 style={{ fontSize: '1.8rem', margin: 0 }}>Advertencia Legal y Responsabilidad</h2>
      </div>
      
      <div style={{ color: 'var(--text-dim)', fontSize: '0.95rem', lineHeight: '1.6' }}>
        <h3 style={{ color: 'var(--text-bright)', marginTop: '20px', fontSize: '1.2rem' }}>Exención sobre la Inteligencia Artificial</h3>
        <p>Gran parte de la programación lógica, empaquetado e ideación estética de este software ha contado con extensa asistencia de Inteligencia Artificial Avanzada. Al usarse herramientas automatizadas y generativas, la arquitectura del código fuente se abastece "TAL CUAL", eximiendo cualquier garantía total de rendimiento perfecto.</p>
        
        <h3 style={{ color: 'var(--text-bright)', marginTop: '20px', fontSize: '1.2rem' }}>Exención sobre el Hub de ROMS Emuladas</h3>
        <p><strong style={{ color: 'var(--text-bright)' }}>Chvstx Nexus NO almacena, aloja, sube ni fomenta la distribución de ficheros de pago, abandonware, ROMs o juegos licenciados bajo Derechos de Autor en sus propios repositorios.</strong></p>
        <p>El módulo <em>Hub de Descarga</em> interno actúa meramente como un explorador automatizado de atajo, dirigiendo tráfico a servidores ajenos de Internet totalmente independientes (tales como <em>retrostic, Myrient o axekin</em>).</p>
        <ul style={{ paddingLeft: '20px', marginTop: '10px' }}>
          <li style={{ marginBottom: '8px' }}>Chvstx Nexus <strong>NO interviene ni se enraiza o relaciona</strong> remotamente con el estado, las caídas o la permanencia de esos portales webs.</li>
          <li><strong>Obligación de Propiedad:</strong> ÚNETE y DESCÁRGATE una ROM sólamente si posees los cartuchos físicos, discos o licencias en tu casa que te otorgan la concesión al <strong>Right of Backup</strong> (Copia de Respaldo). Descargar de estos sitios y distribuirlo es un acto dependiente bajo tu pura y entera responsabilidad sin vinculaciones al equipo o repositorios de Chvstx Nexus.</li>
        </ul>
      </div>
    </section>
  );
};

function App() {
  return (
    <div className="App">
      <Navbar />
      <Hero />
      <Features />
      <Changelog />
      <Community />
      <Donate />
      <Contact />
      <Disclaimer />
      <Footer />
    </div>
  );
}

export default App;
