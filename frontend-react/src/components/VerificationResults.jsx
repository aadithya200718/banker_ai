import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Activity,
  Image as ImageIcon,
} from "lucide-react";

const VerificationResults = ({ result }) => {
  if (!result) return null;

  const {
    similarity_score,
    decision,
    confidence_level,
    detected_variations,
    explanation,
    feature_importance,
    confidence_probability,
    quality,
  } = result;

  const scorePct = Math.round(similarity_score * 100);
  const confidencePct = Math.round((confidence_probability || 0) * 100);

  // Color mapping logic
  const isApprove = decision === "approve";
  const isReview = decision === "manual_review";

  let statusColor = "text-red-500";
  let statusBg = "bg-red-50 border-red-200";
  let StatusIcon = XCircle;

  if (isApprove) {
    statusColor = "text-green-600";
    statusBg = "bg-green-50 border-green-200";
    StatusIcon = CheckCircle;
  } else if (isReview) {
    statusColor = "text-amber-600";
    statusBg = "bg-amber-50 border-amber-200";
    StatusIcon = AlertTriangle;
  }

  const decisionLabel = decision.replace("_", " ").toUpperCase();

  return (
    <div className="space-y-6">
      {/* 1. Score Card */}
      <Card className={`border-2 ${statusBg} shadow-md transition-all`}>
        <CardContent className="pt-8 flex flex-col items-center justify-center text-center">
          <div className="relative h-40 w-40 mb-6">
            <svg
              className="h-full w-full -rotate-90 transform drop-shadow-sm"
              viewBox="0 0 100 100"
            >
              <circle
                className="text-muted/20"
                strokeWidth="6"
                stroke="currentColor"
                fill="transparent"
                r="44"
                cx="50"
                cy="50"
              />
              <circle
                className={statusColor}
                strokeWidth="6"
                strokeDasharray={`${scorePct * 2.76} 276`}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="44"
                cx="50"
                cy="50"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span
                className={`text-4xl font-bold ${statusColor} tracking-tighter`}
              >
                {scorePct}%
              </span>
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1">
                Match
              </span>
            </div>
          </div>

          <div className="flex flex-col items-center gap-3">
            <Badge
              variant={
                isApprove ? "default" : isReview ? "secondary" : "destructive"
              }
              className="px-4 py-1.5 text-sm font-semibold shadow-sm"
            >
              <StatusIcon className="mr-2 h-4 w-4" />
              {decisionLabel}
            </Badge>
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-widest border px-2 py-0.5 rounded-md bg-background/50">
              {confidence_level} CONFIDENCE
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 2. Metrics Grid */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader className="p-4 pb-2">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Activity className="h-4 w-4" />
              <span className="text-xs font-semibold uppercase">
                Confidence
              </span>
            </div>
            <div className="text-2xl font-bold">{confidencePct}%</div>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <Progress value={confidencePct} className="h-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="p-4 pb-2">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <ImageIcon className="h-4 w-4" />
              <span className="text-xs font-semibold uppercase">
                Image Quality
              </span>
            </div>
            <div className="text-2xl font-bold">
              {(quality?.sharpness || 0).toFixed(2)}
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <Progress
              value={(quality?.sharpness || 0) * 100}
              className="h-2 bg-muted"
            />
          </CardContent>
        </Card>
      </div>

      {/* 3. Explanation & Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">AI Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground leading-relaxed bg-muted/50 p-3 rounded-md border border-border">
            {explanation}
          </p>

          {feature_importance && (
            <div className="space-y-3">
              <h4 className="text-xs font-semibold uppercase text-muted-foreground">
                Key Match Factors
              </h4>
              <div className="space-y-2">
                {Object.entries(feature_importance).map(([key, val]) => (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium capitalize">{key}</span>
                      <span className="text-muted-foreground">
                        {Math.round(val * 100)}%
                      </span>
                    </div>
                    <Progress value={val * 100} className="h-1.5" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 4. Variations */}
      {detected_variations && detected_variations.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/50">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm font-semibold text-amber-800 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" /> Detected Variations
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="flex flex-wrap gap-2 mt-2">
              {detected_variations.map((v) => (
                <Badge
                  key={v}
                  variant="outline"
                  className="bg-white border-amber-200 text-amber-700 hover:bg-amber-100"
                >
                  {v.replace("_", " ")}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default VerificationResults;
