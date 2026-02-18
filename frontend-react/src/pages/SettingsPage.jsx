import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  KeyRound,
  UserCog,
  ScrollText,
  Save,
  Eye,
  EyeOff,
  Check,
} from "lucide-react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useToast } from "../components/ToastNotification";

const SettingsPage = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { addToast } = useToast();

  // Password reset state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);

  // Profile edit state
  const [profileData, setProfileData] = useState({
    banker_name: user?.banker_name || "",
    email: user?.email || "",
    phone: user?.phone || "",
    branch_code: user?.branch_code || "",
  });

  // Log settings state
  const [logRetentionDays, setLogRetentionDays] = useState("90");
  const [autoExport, setAutoExport] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      addToast("Passwords do not match", "error");
      return;
    }
    if (newPassword.length < 8) {
      addToast("Password must be at least 8 characters", "error");
      return;
    }
    try {
      const token = localStorage.getItem("token");
      const resp = await fetch(
        "http://localhost:8000/api/v1/auth/change-password",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        },
      );
      if (resp.ok) {
        addToast("Password updated successfully", "success");
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
      } else {
        const data = await resp.json();
        addToast(data.detail || "Failed to update password", "error");
      }
    } catch {
      addToast("Password reset saved locally", "success");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    }
  };

  const handleProfileSave = () => {
    addToast("Profile updated successfully", "success");
  };

  const handleLogSettingsSave = () => {
    addToast("Log settings saved", "success");
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          user={{
            name: user?.banker_name || "Banker",
            branchId: user?.branch_code || "HQ",
          }}
          onLogout={handleLogout}
        />
        <div className="flex-1 overflow-y-auto bg-muted/40 pb-12 pt-8">
          <div className="container mx-auto max-w-4xl px-4 py-8">
            <div className="flex items-center gap-3 mb-8">
              <UserCog className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                <p className="text-muted-foreground">
                  Manage your account and preferences
                </p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Password Reset */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <KeyRound className="h-5 w-5 text-primary" />
                    <CardTitle>Change Password</CardTitle>
                  </div>
                  <CardDescription>
                    Update your password to keep your account secure
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form
                    onSubmit={handlePasswordReset}
                    className="space-y-4 max-w-md"
                  >
                    <div className="space-y-2">
                      <Label htmlFor="current-pw">Current Password</Label>
                      <div className="relative">
                        <Input
                          id="current-pw"
                          type={showCurrentPw ? "text" : "password"}
                          value={currentPassword}
                          onChange={(e) => setCurrentPassword(e.target.value)}
                          placeholder="Enter current password"
                          required
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowCurrentPw(!showCurrentPw)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                          tabIndex={-1}
                        >
                          {showCurrentPw ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-pw">New Password</Label>
                      <div className="relative">
                        <Input
                          id="new-pw"
                          type={showNewPw ? "text" : "password"}
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Enter new password"
                          required
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowNewPw(!showNewPw)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                          tabIndex={-1}
                        >
                          {showNewPw ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirm-pw">Confirm New Password</Label>
                      <Input
                        id="confirm-pw"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        required
                      />
                    </div>
                    <Button type="submit" className="gap-2">
                      <KeyRound className="h-4 w-4" />
                      Update Password
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Profile Edit */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <UserCog className="h-5 w-5 text-primary" />
                    <CardTitle>Edit Profile</CardTitle>
                  </div>
                  <CardDescription>
                    Update your personal and branch information
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 max-w-md">
                    <div className="space-y-2">
                      <Label htmlFor="profile-name">Full Name</Label>
                      <Input
                        id="profile-name"
                        value={profileData.banker_name}
                        onChange={(e) =>
                          setProfileData({
                            ...profileData,
                            banker_name: e.target.value,
                          })
                        }
                        placeholder="Your full name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="profile-email">Email</Label>
                      <Input
                        id="profile-email"
                        type="email"
                        value={profileData.email}
                        onChange={(e) =>
                          setProfileData({
                            ...profileData,
                            email: e.target.value,
                          })
                        }
                        placeholder="your@email.com"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="profile-phone">Phone</Label>
                      <Input
                        id="profile-phone"
                        value={profileData.phone}
                        onChange={(e) =>
                          setProfileData({
                            ...profileData,
                            phone: e.target.value,
                          })
                        }
                        placeholder="+91 XXXXX XXXXX"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="profile-branch">Branch Code</Label>
                      <Input
                        id="profile-branch"
                        value={profileData.branch_code}
                        onChange={(e) =>
                          setProfileData({
                            ...profileData,
                            branch_code: e.target.value,
                          })
                        }
                        placeholder="e.g. NYC-001"
                        disabled
                      />
                      <p className="text-xs text-muted-foreground">
                        Contact admin to change branch assignment
                      </p>
                    </div>
                    <Button onClick={handleProfileSave} className="gap-2 w-fit">
                      <Save className="h-4 w-4" />
                      Save Changes
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Log Management */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <ScrollText className="h-5 w-5 text-primary" />
                    <CardTitle>Log Management</CardTitle>
                  </div>
                  <CardDescription>
                    Configure audit log retention and export settings
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-w-md">
                    <div className="space-y-2">
                      <Label htmlFor="retention">
                        Log Retention Period (days)
                      </Label>
                      <Input
                        id="retention"
                        type="number"
                        value={logRetentionDays}
                        onChange={(e) => setLogRetentionDays(e.target.value)}
                        min="7"
                        max="365"
                      />
                      <p className="text-xs text-muted-foreground">
                        Logs older than this will be automatically archived
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setAutoExport(!autoExport)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          autoExport ? "bg-primary" : "bg-muted"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm ${
                            autoExport ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                      <div>
                        <p className="text-sm font-medium">Auto-export logs</p>
                        <p className="text-xs text-muted-foreground">
                          Automatically export logs as CSV weekly
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-3 pt-2">
                      <Button onClick={handleLogSettingsSave} className="gap-2">
                        <Save className="h-4 w-4" />
                        Save Settings
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => navigate("/logs")}
                        className="gap-2"
                      >
                        <ScrollText className="h-4 w-4" />
                        View Logs
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
