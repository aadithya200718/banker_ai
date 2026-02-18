import React, { useState, useRef, useCallback } from "react";
import Webcam from "react-webcam";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import VerificationResults from "../components/VerificationResults";
import DecisionPanel from "../components/DecisionPanel";
import { verifyIdentity } from "../services/api";
import { useToast } from "../components/ToastNotification";
import { useAuth } from "../hooks/useAuth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Camera,
  Upload,
  X,
  ArrowLeft,
  Loader2,
  ScanFace,
  FileText,
  ScrollText,
  User,
} from "lucide-react";

const Dashboard = () => {
  const [liveImage, setLiveImage] = useState(null);
  const [refImage, setRefImage] = useState(null);
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [personName, setPersonName] = useState("");
  const [personAge, setPersonAge] = useState("");
  const [personGender, setPersonGender] = useState("");

  const webcamRef = useRef(null);
  const { addToast } = useToast();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handleCapture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setLiveImage(imageSrc);
    setCameraActive(false);
  }, [webcamRef]);

  const handleRefUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        addToast("Reference image too large (max 5MB)", "error");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => setRefImage(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleLiveUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => setLiveImage(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const reset = () => {
    setLiveImage(null);
    setRefImage(null);
    setUserId("");
    setResult(null);
    setCameraActive(false);
    setPersonName("");
    setPersonAge("");
    setPersonGender("");
  };

  const handleVerify = async () => {
    if (!liveImage || (!refImage && !userId)) {
      addToast("Please provide reference ID and live photo", "warning");
      return;
    }

    setLoading(true);
    try {
      // Convert base64 to blob
      const liveBlob = await (await fetch(liveImage)).blob();
      const refBlob = refImage ? await (await fetch(refImage)).blob() : null;

      const response = await verifyIdentity(liveBlob, refBlob, userId);
      setResult(response.data);
      addToast("Verification complete", "success");
    } catch (err) {
      console.error(err);
      addToast(err.response?.data?.detail || "Verification failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          user={{
            name: user?.banker_name || "Banker",
            branchId: user?.branch_code || "HQ",
          }}
          onLogout={handleLogout}
        />
        <div className="flex-1 overflow-y-auto bg-muted/40 pb-12 pt-8">
          <div className="container mx-auto max-w-6xl px-4 py-8">
            {!result ? (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="mb-8 flex items-center justify-between">
                  <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">
                      New Verification
                    </h1>
                    <p className="text-lg text-muted-foreground">
                      Upload a reference ID and capture a live image to verify
                      identity.
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => navigate("/logs")}
                    className="gap-2 shadow-sm"
                  >
                    <ScrollText className="h-4 w-4" />
                    View Audit Logs
                  </Button>
                </div>

                <div className="grid gap-8 lg:grid-cols-2">
                  {/* Left Column: Reference ID */}
                  <Card className="border-t-4 border-t-foreground shadow-sm transition-all hover:shadow-md">
                    <CardHeader className="bg-muted/20 pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="rounded-full bg-background border p-2 text-foreground shadow-sm">
                            <FileText className="h-5 w-5" />
                          </div>
                          <CardTitle className="text-xl">
                            Reference ID
                          </CardTitle>
                        </div>
                        <Badge
                          variant="outline"
                          className="bg-background font-mono text-xs uppercase"
                        >
                          Required
                        </Badge>
                      </div>
                      <CardDescription>
                        Government issued ID Card or Passport
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-6">
                      {!refImage ? (
                        <div
                          className="group relative flex h-64 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-muted-foreground/25 bg-muted/10 transition-colors hover:border-primary hover:bg-primary/5"
                          onClick={() =>
                            document.getElementById("reference-upload").click()
                          }
                        >
                          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-background shadow-sm ring-1 ring-border group-hover:scale-110 transition-transform">
                            <Upload className="h-8 w-8 text-muted-foreground group-hover:text-primary" />
                          </div>
                          <p className="mt-4 text-sm font-medium text-muted-foreground group-hover:text-primary">
                            Click to upload document
                          </p>
                          <p className="text-xs text-muted-foreground/70">
                            JPG, PNG up to 5MB
                          </p>
                          <Input
                            id="reference-upload"
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={handleRefUpload}
                          />
                        </div>
                      ) : (
                        <div className="relative overflow-hidden rounded-xl border bg-background shadow-sm">
                          <img
                            src={refImage}
                            alt="Reference"
                            className="h-64 w-full object-contain p-2"
                          />
                          <Button
                            variant="destructive"
                            size="icon"
                            className="absolute right-2 top-2 h-8 w-8 rounded-full shadow-md"
                            onClick={() => setRefImage(null)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Right Column: Live Person */}
                  <Card className="border-t-4 border-t-foreground shadow-sm transition-all hover:shadow-md">
                    <CardHeader className="bg-muted/20 pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="rounded-full bg-background border p-2 text-foreground shadow-sm">
                            <ScanFace className="h-5 w-5" />
                          </div>
                          <CardTitle className="text-xl">Live Person</CardTitle>
                        </div>
                        <Badge
                          variant="outline"
                          className="bg-background font-mono text-xs uppercase"
                        >
                          Required
                        </Badge>
                      </div>
                      <CardDescription>
                        Real-time capture or recent photo
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-6">
                      {!liveImage ? (
                        cameraActive ? (
                          <div className="overflow-hidden rounded-xl border bg-black shadow-inner">
                            <Webcam
                              ref={webcamRef}
                              screenshotFormat="image/jpeg"
                              className="h-64 w-full object-cover"
                            />
                            <div className="flex justify-center bg-background/90 p-4">
                              <Button
                                onClick={handleCapture}
                                className="gap-2 font-semibold"
                              >
                                <Camera className="h-4 w-4" /> Capture Photo
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div className="flex h-64 flex-col items-center justify-center rounded-xl border-2 border-dashed border-muted-foreground/25 bg-muted/10 p-6 text-center">
                            <div className="mb-4 rounded-full bg-background p-4 shadow-sm ring-1 ring-border">
                              <Camera className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="mb-1 text-lg font-semibold">
                              Take Photo
                            </h3>
                            <p className="mb-6 text-sm text-muted-foreground">
                              Use your camera or upload a file
                            </p>
                            <div className="flex gap-3">
                              <Button
                                onClick={() => setCameraActive(true)}
                                className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-md transition-all hover:-translate-y-0.5"
                              >
                                <Camera className="mr-2 h-4 w-4" /> Use Camera
                              </Button>
                              <div className="relative flex items-center px-2">
                                <span className="text-xs font-bold text-muted-foreground uppercase">
                                  OR
                                </span>
                              </div>
                              <Button
                                variant="outline"
                                onClick={() =>
                                  document.getElementById("live-upload").click()
                                }
                                className="shadow-sm hover:bg-accent"
                              >
                                <Upload className="mr-2 h-4 w-4" /> Upload File
                              </Button>
                              <Input
                                id="live-upload"
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={handleLiveUpload}
                              />
                            </div>
                          </div>
                        )
                      ) : (
                        <div className="relative overflow-hidden rounded-xl border bg-background shadow-sm">
                          <img
                            src={liveImage}
                            alt="Live"
                            className="h-64 w-full object-contain p-2"
                          />
                          <Button
                            variant="destructive"
                            size="icon"
                            className="absolute right-2 top-2 h-8 w-8 rounded-full shadow-md"
                            onClick={() => setLiveImage(null)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Person Details */}
                <Card className="border-t-4 border-t-primary/50 shadow-sm transition-all hover:shadow-md">
                  <CardHeader className="bg-muted/20 pb-4">
                    <div className="flex items-center gap-2">
                      <div className="rounded-full bg-background border p-2 text-foreground shadow-sm">
                        <User className="h-5 w-5" />
                      </div>
                      <CardTitle className="text-xl">Person Details</CardTitle>
                    </div>
                    <CardDescription>
                      Details of the person being verified
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="grid gap-4 sm:grid-cols-3">
                      <div className="space-y-2">
                        <Label htmlFor="person-name">Full Name</Label>
                        <Input
                          id="person-name"
                          value={personName}
                          onChange={(e) => setPersonName(e.target.value)}
                          placeholder="e.g. Raj Kumar"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="person-age">Age</Label>
                        <Input
                          id="person-age"
                          type="number"
                          min="1"
                          max="120"
                          value={personAge}
                          onChange={(e) => setPersonAge(e.target.value)}
                          placeholder="e.g. 28"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="person-gender">Gender</Label>
                        <select
                          id="person-gender"
                          value={personGender}
                          onChange={(e) => setPersonGender(e.target.value)}
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                        >
                          <option value="">Select</option>
                          <option value="Male">Male</option>
                          <option value="Female">Female</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Action Bar */}
                <div className="mt-8 flex justify-end">
                  <Button
                    size="lg"
                    onClick={handleVerify}
                    disabled={!refImage || !liveImage || loading}
                    className="h-12 min-w-[200px] gap-2 rounded-full px-8 text-base font-bold shadow-lg transition-all hover:scale-105 hover:shadow-xl disabled:opacity-50 disabled:hover:scale-100"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />{" "}
                        Verifying...
                      </>
                    ) : (
                      <>
                        Verify Identity <ScanFace className="ml-2 h-5 w-5" />
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ) : (
              /* Results View */
              <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-4">
                  <Button variant="outline" onClick={reset} className="gap-2">
                    <ArrowLeft className="h-4 w-4" /> New Verification
                  </Button>
                  <h2 className="text-2xl font-bold tracking-tight text-foreground">
                    Verification Report
                  </h2>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2 space-y-6">
                    <VerificationResults result={result} />
                  </div>

                  <div className="lg:col-span-1">
                    <div className="sticky top-24">
                      <DecisionPanel
                        result={result}
                        onDecisionComplete={() => {
                          addToast("Decision recorded successfully", "success");
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
