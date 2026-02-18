import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollText, Search, ArrowLeft } from "lucide-react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

const sampleLogs = [
  {
    id: 1,
    timestamp: "2026-02-16 18:15:22",
    action: "VERIFICATION",
    status: "SUCCESS",
    decision: "APPROVE",
    similarity: 85,
    confidence: "HIGH",
    reason: "Strong facial match detected",
  },
  {
    id: 2,
    timestamp: "2026-02-16 17:45:10",
    action: "VERIFICATION",
    status: "SUCCESS",
    decision: "REJECT",
    similarity: 45,
    confidence: "LOW",
    reason: "Low similarity score",
  },
  {
    id: 3,
    timestamp: "2026-02-16 16:30:05",
    action: "VERIFICATION",
    status: "FAILED",
    decision: "ERROR",
    similarity: 0,
    confidence: "N/A",
    reason: "Face processing failed: No face detected",
  },
];

const AuditLogsPage = () => {
  const [filter, setFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const filteredLogs = sampleLogs.filter((log) => {
    if (filter !== "all" && log.decision !== filter) return false;
    if (
      searchTerm &&
      !log.reason.toLowerCase().includes(searchTerm.toLowerCase())
    )
      return false;
    return true;
  });

  const getStatusBadge = (decision) => {
    const variants = {
      APPROVE: "default",
      REJECT: "destructive",
      REVIEW: "secondary",
      ERROR: "outline",
    };
    return variants[decision] || "outline";
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
          <div className="container mx-auto max-w-7xl px-4 py-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <ScrollText className="h-8 w-8 text-primary" />
                <div>
                  <h1 className="text-3xl font-bold tracking-tight">
                    Audit Logs
                  </h1>
                  <p className="text-muted-foreground">
                    View verification history and decisions
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                onClick={() => navigate("/dashboard")}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-4 items-center">
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search by reason..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {["all", "APPROVE", "REJECT", "REVIEW"].map((f) => (
                      <Button
                        key={f}
                        variant={filter === f ? "default" : "outline"}
                        size="sm"
                        onClick={() => setFilter(f)}
                      >
                        {f === "all" ? "All" : f}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Logs Table */}
            <Card>
              <CardHeader>
                <CardTitle>Verification History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3 text-sm font-semibold">
                          Timestamp
                        </th>
                        <th className="text-left p-3 text-sm font-semibold">
                          Status
                        </th>
                        <th className="text-left p-3 text-sm font-semibold">
                          Decision
                        </th>
                        <th className="text-left p-3 text-sm font-semibold">
                          Similarity
                        </th>
                        <th className="text-left p-3 text-sm font-semibold">
                          Confidence
                        </th>
                        <th className="text-left p-3 text-sm font-semibold">
                          Reason
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredLogs.map((log) => (
                        <tr
                          key={log.id}
                          className="border-b hover:bg-accent/50 transition-colors"
                        >
                          <td className="p-3 text-sm font-mono">
                            {log.timestamp}
                          </td>
                          <td className="p-3">
                            <Badge
                              variant={
                                log.status === "SUCCESS"
                                  ? "default"
                                  : "destructive"
                              }
                            >
                              {log.status}
                            </Badge>
                          </td>
                          <td className="p-3">
                            <Badge variant={getStatusBadge(log.decision)}>
                              {log.decision}
                            </Badge>
                          </td>
                          <td className="p-3 text-sm font-semibold">
                            {log.similarity}%
                          </td>
                          <td className="p-3 text-sm">{log.confidence}</td>
                          <td className="p-3 text-sm text-muted-foreground">
                            {log.reason}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {filteredLogs.length === 0 && (
                    <div className="text-center py-12 text-muted-foreground">
                      No logs found matching your filters
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditLogsPage;
