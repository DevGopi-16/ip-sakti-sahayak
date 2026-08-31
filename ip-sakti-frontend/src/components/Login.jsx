
import React, { useEffect, useState } from 'react';
import { loginWithGoogle } from '../firebase';

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [mouse, setMouse] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const move = (e) => {
      setMouse({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      });
    };

    window.addEventListener('mousemove', move);
    return () => window.removeEventListener('mousemove', move);
  }, []);

  const handleLogin = async () => {
    if (loading) return;

    try {
      setLoading(true);
      await loginWithGoogle();
    } catch (error) {
      console.error('Authentication Error:', error);
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#020202] text-white">

      <div className="pointer-events-none absolute inset-0">

        <div
          className="absolute left-1/2 top-[55%] h-[700px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[140px]"
          style={{
            background:
              'radial-gradient(circle, rgba(245,158,11,0.12), transparent 68%)',
          }}
        />
        <div
          className="absolute h-[500px] w-[500px] rounded-full blur-[120px] transition-transform duration-700"
          style={{
            left: `calc(50% + ${mouse.x * 180}px)`,
            top: `calc(50% + ${mouse.y * 120}px)`,
            background:
              'radial-gradient(circle, rgba(251,191,36,0.055), transparent 65%)',
          }}
        />
        <div className="absolute bottom-[-300px] left-1/2 h-[650px] w-[900px] -translate-x-1/2 rounded-full bg-amber-500/[0.06] blur-[100px]" />
        <div
          className="absolute inset-0 opacity-[0.045]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(245,158,11,0.8) 1px, transparent 1px),
              linear-gradient(90deg, rgba(245,158,11,0.8) 1px, transparent 1px)
            `,
            backgroundSize: '65px 65px',
            maskImage:
              'radial-gradient(circle at center, black 0%, transparent 75%)',
            WebkitMaskImage:
              'radial-gradient(circle at center, black 0%, transparent 75%)',
          }}
        />

        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_20%,rgba(0,0,0,0.72)_100%)]" />
      </div>

      <div
        className="pointer-events-none absolute left-1/2 top-1/2 h-[900px] w-[900px] -translate-x-1/2 -translate-y-1/2"
        style={{
          transform: `translate(-50%, -50%) rotateX(${
            mouse.y * -3
          }deg) rotateY(${mouse.x * 3}deg)`,
          transition: 'transform 1s ease-out',
        }}
      >
        <div className="absolute inset-[8%] rounded-full border border-amber-400/[0.055] animate-[spin_55s_linear_infinite]" />

        <div className="absolute inset-[20%] rounded-full border border-amber-400/[0.07] animate-[spin_38s_linear_infinite_reverse]" />

        <div className="absolute inset-[32%] rounded-full border border-amber-400/[0.08] animate-[spin_25s_linear_infinite]" />

        <div className="absolute inset-[42%] rounded-full border border-dashed border-amber-400/[0.09] animate-[spin_18s_linear_infinite_reverse]" />
      </div>

      <div className="pointer-events-none absolute inset-0">
        {Array.from({ length: 45 }).map((_, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-amber-300/40"
            style={{
              width: `${i % 4 === 0 ? 2 : 1}px`,
              height: `${i % 4 === 0 ? 2 : 1}px`,
              left: `${(i * 47.3) % 100}%`,
              top: `${(i * 29.7) % 100}%`,
              animation: `pulse ${
                2 + (i % 5)
              }s ease-in-out ${i * 0.12}s infinite`,
            }}
          />
        ))}
      </div>

      <header className="absolute left-0 right-0 top-0 z-30 flex items-center justify-between px-6 py-6 md:px-10">

        <div className="flex items-center gap-3">

          <div className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-amber-400/25 bg-amber-400/[0.07] shadow-[0_0_30px_rgba(245,158,11,0.1)]">

            <img
              src="/logo.png"
              alt="IP-SAKTI"
              className="h-8 w-8 object-contain"
            />

            <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.9)]" />
          </div>

          <div>
            <div className="text-sm font-bold tracking-[0.22em] text-amber-400">
              IP-SAKTI
            </div>

            <div className="text-[10px] tracking-[0.32em] text-white/40">
              SAHAYAK
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-amber-400/15 bg-white/[0.035] px-4 py-2 backdrop-blur-xl">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
          </span>

          <span className="text-[10px] font-medium tracking-[0.18em] text-amber-300/80">
            AI CORE ONLINE
          </span>
        </div>
      </header>

      <main className="relative z-20 flex min-h-screen items-center justify-center px-5 py-28">
        <div className="w-full max-w-[1180px]">
          <div className="grid items-center gap-8 lg:grid-cols-[1fr_470px_1fr]">
            <div className="hidden space-y-4 lg:block">

              <FeatureCard
                number="01"
                icon="◈"
                title="AI LEGAL RESEARCH"
                description="Natural-language research across Indian intellectual property laws."
              />

              <FeatureCard
                number="02"
                icon="◇"
                title="SECURE & CONFIDENTIAL"
                description="Authentication and protected personal conversation history."
              />

              <FeatureCard
                number="03"
                icon="ϟ"
                title="FAST RESPONSES"
                description="AI-powered answers designed for rapid legal research."
              />

            </div>

            <section className="relative">
              <div className="absolute -inset-12 rounded-[50px] bg-amber-500/[0.045] blur-[70px]" />

              <div
                className="relative overflow-hidden rounded-[34px] border border-amber-300/[0.18] bg-[#090909]/80 p-8 shadow-[0_35px_120px_rgba(0,0,0,0.8)] backdrop-blur-2xl sm:p-10"
                style={{
                  transform: `perspective(1200px) rotateX(${
                    mouse.y * -1.2
                  }deg) rotateY(${mouse.x * 1.2}deg)`,
                  transition: 'transform 0.5s ease-out',
                }}
              >

                <div className="absolute left-1/2 top-0 h-px w-[75%] -translate-x-1/2 bg-gradient-to-r from-transparent via-amber-300/80 to-transparent" />

                <div className="absolute left-0 top-0 h-[1px] w-1/3 animate-[scan_5s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-amber-300 to-transparent opacity-70" />

                <div className="pointer-events-none absolute inset-3 rounded-[27px] border border-white/[0.025]" />

                <div className="relative mx-auto mb-8 h-28 w-28">

                  <div className="absolute inset-0 rounded-[32px] border border-amber-400/15 animate-[spin_14s_linear_infinite]" />

                  <div className="absolute inset-3 rounded-[27px] border border-dashed border-amber-400/20 animate-[spin_9s_linear_infinite_reverse]" />

                  <div className="absolute inset-7 rounded-2xl bg-amber-400/[0.04] shadow-[0_0_60px_rgba(245,158,11,0.15)]" />

                  <div className="absolute left-1/2 top-1/2 flex h-[62px] w-[62px] -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-2xl border border-amber-300/30 bg-gradient-to-br from-amber-300 via-amber-400 to-amber-600 shadow-[0_0_45px_rgba(245,158,11,0.28)]">
                    <img
                      src="/logo.png"
                      alt="IP-SAKTI"
                      className="h-12 w-12 object-contain"
                    />
                  </div>

                  <span className="absolute left-1/2 top-[-3px] h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.9)]" />

                  <span className="absolute bottom-[-3px] left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.9)]" />

                  <span className="absolute left-[-3px] top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.9)]" />

                  <span className="absolute right-[-3px] top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.9)]" />
                </div>

                <div className="text-center">

                  <div className="mb-3 text-[9px] font-semibold tracking-[0.42em] text-amber-400/60">
                    INTELLIGENT LEGAL SYSTEM
                  </div>

                  <h1 className="text-[38px] font-black tracking-[-0.03em] sm:text-[44px]">

                    <span className="bg-gradient-to-r from-amber-200 via-yellow-400 to-amber-500 bg-clip-text text-transparent">
                      IP-SAKTI
                    </span>

                    <span className="text-white">
                      {' '}Sahayak
                    </span>

                  </h1>

                  <p className="mx-auto mt-5 max-w-[380px] text-[13px] leading-6 text-white/40">
                    AI Legal Assistant for Indian Intellectual Property &
                    Traditional Knowledge Laws
                  </p>
                </div>

                <div className="mt-7 grid grid-cols-2 gap-2">

                  <Status label="KNOWLEDGE ENGINE" />

                  <Status label="AI REASONING" />

                  <Status label="LEGAL DATABASE" />

                  <Status label="AUTHENTICATION" />

                </div>
                <div className="mt-7">

                  <button
                    onClick={handleLogin}
                    disabled={loading}
                    className="group relative flex w-full items-center justify-center gap-3 overflow-hidden rounded-2xl border border-white/[0.12] bg-white/[0.065] px-5 py-4 text-sm font-medium text-white shadow-[0_15px_40px_rgba(0,0,0,0.3)] transition-all duration-300 hover:-translate-y-0.5 hover:border-amber-300/40 hover:bg-white/[0.09] hover:shadow-[0_0_40px_rgba(245,158,11,0.1)] disabled:cursor-not-allowed disabled:opacity-60"
                  >

                    <span className="absolute inset-y-0 -left-full w-1/3 skew-x-[-20deg] bg-gradient-to-r from-transparent via-white/10 to-transparent transition-all duration-700 group-hover:left-[130%]" />

                    {loading ? (
                      <>
                        <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/20 border-t-amber-400" />
                        <span>Authenticating...</span>
                      </>
                    ) : (
                      <>
                        <GoogleIcon />

                        <span>
                          Continue with Google
                        </span>

                        <span className="ml-auto text-white/20 transition-all duration-300 group-hover:translate-x-1 group-hover:text-amber-400">
                          →
                        </span>
                      </>
                    )}

                  </button>

                </div>
                <div className="mt-6 flex items-center justify-center gap-2 text-[9px] tracking-[0.15em] text-white/25">
                  <span className="text-emerald-400">●</span>
                  FIREBASE AUTHENTICATION · SECURE SESSION
                </div>

                <p className="mt-6 text-center text-[9px] leading-5 text-white/20">
                  IP-SAKTI Sahayak provides statutory reference for
                  legal research. Always verify information with
                  qualified legal professionals.
                </p>

              </div>
            </section>

            <div className="hidden space-y-4 lg:block">

              <FeatureCard
                number="04"
                icon="▤"
                title="MULTI-LAW COVERAGE"
                description="Designed around multiple Indian intellectual property law domains."
              />

              <FeatureCard
                number="05"
                icon="◎"
                title="INDIAN JURISDICTION"
                description="Focused on Indian legal frameworks and traditional knowledge."
              />

              <FeatureCard
                number="06"
                icon="▥"
                title="SMART ANALYTICS"
                description="Transform complex legal information into understandable answers."
              />

            </div>

          </div>

          <div className="mx-auto mt-10 hidden max-w-[950px] items-center justify-between rounded-2xl border border-white/[0.06] bg-white/[0.025] px-6 py-4 backdrop-blur-xl md:flex">

            <div className="flex items-center gap-3">

              <span className="relative flex h-2 w-2">
                <span className="absolute h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
                <span className="relative h-2 w-2 rounded-full bg-emerald-400" />
              </span>

              <span className="text-[10px] tracking-[0.12em] text-white/35">
                SYSTEM STATUS · ALL SYSTEMS OPERATIONAL
              </span>

            </div>

            <div className="flex items-center gap-7 text-[9px] tracking-[0.16em] text-white/25">

              <span>
                <b className="text-amber-400/70">AI</b> POWERED
              </span>

              <span>
                <b className="text-amber-400/70">INDIA</b> FOCUSED
              </span>

              <span>
                <b className="text-amber-400/70">24/7</b> ACCESS
              </span>

            </div>

            <div className="text-[10px] text-white/30">
              🛡 SECURE ACCESS
            </div>

          </div>

        </div>
      </main>

      <div className="absolute bottom-5 left-0 right-0 z-20 text-center text-[9px] tracking-[0.18em] text-white/20 md:hidden">
        IP-SAKTI · AI LEGAL INTELLIGENCE
      </div>

      <style>{`
        @keyframes scan {
          0% {
            transform: translateX(-150%);
            opacity: 0;
          }

          20% {
            opacity: 1;
          }

          50% {
            transform: translateX(450%);
            opacity: 0.8;
          }

          100% {
            transform: translateX(450%);
            opacity: 0;
          }
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        @keyframes pulse {
          0%,
          100% {
            opacity: 0.15;
            transform: scale(0.8);
          }

          50% {
            opacity: 0.8;
            transform: scale(1.5);
          }
        }
      `}</style>
    </div>
  );
}

function FeatureCard({ number, icon, title, description }) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.025] p-5 backdrop-blur-xl transition-all duration-500 hover:-translate-y-1 hover:border-amber-400/20 hover:bg-white/[0.045]">

      <div className="absolute inset-y-0 left-0 w-px bg-gradient-to-b from-transparent via-amber-400/60 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

      <div className="mb-4 flex items-center justify-between">

        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-amber-400/15 bg-amber-400/[0.045] text-lg text-amber-400 transition-transform duration-500 group-hover:scale-110">
          {icon}
        </div>

        <span className="text-[9px] tracking-[0.2em] text-white/15">
          {number}
        </span>

      </div>

      <h3 className="text-[11px] font-bold tracking-[0.12em] text-white/75">
        {title}
      </h3>

      <p className="mt-2 text-[11px] leading-5 text-white/30">
        {description}
      </p>

    </div>
  );
}

function Status({ label }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-white/[0.045] bg-white/[0.018] px-3 py-2">

      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.7)]" />

      <span className="text-[7px] tracking-[0.1em] text-white/25">
        {label}
      </span>

    </div>
  );
}

function GoogleIcon() {
  return (
    <svg
      className="h-5 w-5"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        fill="#EA4335"
        d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z"
      />

      <path
        fill="#4285F4"
        d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"
      />

      <path
        fill="#FBBC05"
        d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12 0 14.3s.7 4.6 1.9 7l3.7-2.9z"
      />

      <path
        fill="#34A853"
        d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z"
      />
    </svg>
  );
}

