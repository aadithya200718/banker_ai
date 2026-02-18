import React, { useState } from "react";
import { submitDecision } from "../services/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Check, X, RotateCcw, ShieldCheck } from "lucide-react";

const DecisionPanel = ({ result, onDecisionComplete }) => {
  const [reasoning, setReasoning] = useState("");
  const [loading, setLoading] = useState(false);
  const [completedAction, setCompletedAction] = useState(null);

  if (!result || completedAction) {
    if (completedAction) {
      return (
        <Card className="border-green-200 bg-green-50/50">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto bg-green-100 p-2 rounded-full mb-2 w-fit">
              <Check className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle className="text-green-700">Decision Recorded</CardTitle>
          </CardHeader>
          <CardContent className="text-center text-green-700/80 pb-6">
            <p>
              You {completedAction.toLowerCase().replace("banker_", "")}d this
              verification.
            </p>
          </CardContent>
        </Card>
      );
    }
    return null;
  }

  const { decision_id, recommendation } = result;

  const handleDecision = async (action) => {
    if (!decision_id) return;

    setLoading(true);
    try {
      await submitDecision(decision_id, action, reasoning);
      setCompletedAction(action);
      if (onDecisionComplete) onDecisionComplete();
    } catch (err) {
      console.error(err);
      alert("Failed to submit decision");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="h-full flex flex-col shadow-md border-t-4 border-t-foreground">
      <CardHeader className="pb-4 bg-muted/20 border-b">
        <div className="flex items-center gap-2 mb-2">
          <div className="bg-background border p-1.5 rounded-md shadow-sm">
            <ShieldCheck className="h-4 w-4 text-foreground" />
          </div>
          <span className="text-xs font-bold text-foreground uppercase tracking-wider">
            Banker Actions
          </span>
        </div>
        <CardTitle className="text-xl">Make Decision</CardTitle>
        <CardDescription className="text-muted-foreground font-medium leading-relaxed">
          {recommendation}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 pt-6 space-y-6">
        <div className="space-y-3">
          <Label className="text-xs uppercase text-muted-foreground font-bold tracking-wider">
            Notes / Reasoning
          </Label>
          <Textarea
            className="resize-none h-32 bg-background border-muted focus:border-primary transition-colors"
            placeholder="Add context to your decision (e.g. 'Verified physical ID looks authentic')..."
            value={reasoning}
            onChange={(e) => setReasoning(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Button
            onClick={() => handleDecision("BANKER_APPROVE")}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white shadow-sm hover:shadow-md transition-all"
          >
            {loading ? (
              "..."
            ) : (
              <>
                <Check className="mr-2 h-4 w-4" /> Approve
              </>
            )}
          </Button>

          <Button
            onClick={() => handleDecision("BANKER_REJECT")}
            disabled={loading}
            variant="destructive"
            className="shadow-sm hover:shadow-md transition-all"
          >
            {loading ? (
              "..."
            ) : (
              <>
                <X className="mr-2 h-4 w-4" /> Reject
              </>
            )}
          </Button>
        </div>
      </CardContent>

      <CardFooter className="pt-2 pb-6">
        <Button
          variant="outline"
          className="w-full text-muted-foreground hover:text-foreground hover:bg-muted/50 border-dashed"
          disabled={loading}
          onClick={() => handleDecision("REQUEST_RECAPTURE")}
        >
          <RotateCcw className="mr-2 h-4 w-4" /> Request Re-capture
        </Button>
      </CardFooter>
    </Card>
  );
};

export default DecisionPanel;
