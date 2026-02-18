import React, { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useNavigate, Link } from "react-router-dom";
import { useToast } from "./ToastNotification";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ShieldCheck, Check, Lock, Eye, EyeOff } from "lucide-react";

const LoginForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const { login, loading } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      addToast("Welcome back, Banker!", "success");
      navigate("/dashboard");
    } catch (err) {
      const msg = err.response?.data?.detail;
      const text = typeof msg === "string" ? msg : msg?.[0]?.msg || err.message || "Login failed";
      addToast(text, "error");
    }
  };

  return (
    <div className="auth-page-wrapper flex min-h-screen w-full overflow-hidden bg-background lg:grid lg:grid-cols-2">
      {/* Left Panel: Premium Branding */}
      <div className="auth-brand-panel relative hidden min-h-screen flex-col justify-between overflow-hidden p-14 lg:flex">
        <div className="absolute inset-0">
          <div
            className="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-emerald-500/20 blur-3xl"
            style={{ animation: "float 12s ease-in-out infinite" }}
          />
          <div
            className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-teal-600/15 blur-3xl"
            style={{ animation: "float 15s ease-in-out infinite 2s" }}
          />
          <div
            className="absolute right-1/2 top-1/2 h-64 w-64 -translate-y-1/2 rounded-full bg-cyan-500/10 blur-3xl"
            style={{ animation: "float 18s ease-in-out infinite 4s" }}
          />
        </div>

        <div className="relative z-10">
          <div className="mb-10 flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10 shadow-lg backdrop-blur-xl ring-1 ring-white/20">
              <ShieldCheck className="h-8 w-8 text-emerald-400" />
            </div>
            <h1 className="font-outfit text-3xl font-bold tracking-tight text-white">
              Banker Verify
            </h1>
          </div>
          <p className="max-w-md text-lg leading-relaxed text-slate-300">
            Enterprise-grade identity assurance platform powered by advanced
            biometric verification and real-time fraud detection.
          </p>
        </div>

        <div className="relative z-10 space-y-5">
          {[
            "Facial Biometrics Engine",
            "Real-time Fraud Detection",
            "Secure Audit Trail",
          ].map((item, i) => (
            <div
              key={item}
              className="flex items-center gap-3"
              style={{ animation: `fade-up 0.6s ease-out ${i * 0.1}s both` }}
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 ring-1 ring-emerald-400/30">
                <Check className="h-5 w-5 text-emerald-400" strokeWidth={2.5} />
              </div>
              <span className="font-medium text-slate-200">{item}</span>
            </div>
          ))}
        </div>

        <p className="relative z-10 text-sm text-slate-500">
          © {new Date().getFullYear()} Banker Verify. All rights reserved.
        </p>
      </div>

      {/* Right Panel: Form */}
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-muted/30 to-background p-6 lg:p-12">
        <Card
          className="auth-card w-full max-w-md animate-[fade-up_0.5s_ease-out]"
          style={{ animationDelay: "0.1s" }}
        >
          <CardHeader className="space-y-2 pb-6">
            <div className="mb-4 flex items-center gap-2 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                <ShieldCheck className="h-6 w-6 text-primary" />
              </div>
              <span className="font-outfit text-xl font-bold">Banker Verify</span>
            </div>
            <CardTitle className="font-outfit text-2xl font-bold tracking-tight">
              Welcome back
            </CardTitle>
            <CardDescription className="text-base text-muted-foreground">
              Sign in to access your verification portal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="font-medium">
                  Email
                </Label>
                <div className="auth-input-focus group relative rounded-lg">
                  <Input
                    id="email"
                    type="email"
                    placeholder="banker@bank.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoFocus
                    disabled={loading}
                    className="h-12 border-0 bg-muted/50 py-6 text-black dark:text-white transition-all placeholder:text-muted-foreground/60 focus-visible:ring-2 focus-visible:ring-emerald-500/50 dark:bg-muted/30"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="font-medium">
                  Password
                </Label>
                <div className="auth-input-focus group relative rounded-lg">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={loading}
                    className="h-12 border-0 bg-muted/50 py-6 pr-12 text-black dark:text-white transition-all placeholder:text-muted-foreground/60 focus-visible:ring-2 focus-visible:ring-emerald-500/50 dark:bg-muted/30"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    tabIndex={-1}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
              <Button
                type="submit"
                className="h-12 w-full font-semibold shadow-lg shadow-emerald-500/25 transition-all hover:shadow-emerald-500/40 dark:shadow-emerald-900/30"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Signing in...
                  </>
                ) : (
                  "Sign in"
                )}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-4 border-t border-border/50 bg-muted/20 px-6 py-5">
            <div className="flex w-full items-center justify-center gap-2 text-sm">
              <span className="text-muted-foreground">New to Banker Verify?</span>
              <Link
                to="/register"
                className="font-semibold text-emerald-600 transition-colors hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
              >
                Create account
              </Link>
            </div>
            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <Lock className="h-3.5 w-3.5" />
              256-bit encryption • All actions logged
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default LoginForm;
