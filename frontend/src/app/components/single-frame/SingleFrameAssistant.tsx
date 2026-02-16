import React from "react";
import { Brain, MessageCircle, Send, Sparkles } from "lucide-react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";

type SingleFrameAssistantProps = {
  hasPredictions: boolean;
  chatQuestion: string;
  chatResponse: string;
  chatLoading: boolean;
  quickQuestions: string[];
  onQuestionChange: (value: string) => void;
  onAsk: () => void;
  onQuickQuestion: (value: string) => void;
};

export const SingleFrameAssistant: React.FC<SingleFrameAssistantProps> = ({
  hasPredictions,
  chatQuestion,
  chatResponse,
  chatLoading,
  quickQuestions,
  onQuestionChange,
  onAsk,
  onQuickQuestion,
}) => {
  return (
    <div className="border-t-2 border-slate-200 dark:border-slate-700/50 pt-8">
      <div className="relative bg-gradient-to-br from-slate-50 to-white dark:from-slate-800/50 dark:to-slate-900/50 rounded-xl p-8 border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl shadow-lg">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl text-slate-900 dark:text-white">
              AI Assistant
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {hasPredictions
                ? "Ask about the detected defect"
                : "Ask about metal types"}
            </p>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Textarea
              value={chatQuestion}
              onChange={(e) => onQuestionChange(e.target.value)}
              placeholder={
                hasPredictions
                  ? "e.g., What causes this defect?"
                  : "e.g., What is steel?"
              }
              className="min-h-[120px] bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-xl resize-none"
              onKeyDown={(e) =>
                e.key === "Enter" &&
                !e.shiftKey &&
                (e.preventDefault(), onAsk())
              }
            />
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 uppercase">
                Quick Questions
              </p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => onQuickQuestion(q)}
                    className="text-xs px-3 py-2 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-all hover:scale-105"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
            <Button
              onClick={onAsk}
              disabled={chatLoading || !chatQuestion.trim()}
              className="w-full bg-gradient-to-r from-slate-700 to-slate-900 text-white"
            >
              {chatLoading ? (
                <>
                  <MessageCircle className="w-4 h-4 mr-2 animate-pulse" />
                  Thinking...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Ask AI Assistant
                </>
              )}
            </Button>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border-2 border-slate-200 dark:border-slate-700 min-h-[300px] max-h-[400px] overflow-y-auto">
            {chatResponse ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-700">
                  <Sparkles className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                  <span className="text-xs text-slate-600 dark:text-slate-400 uppercase">
                    AI Response
                  </span>
                </div>
                <pre className="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {chatResponse}
                </pre>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400">
                <MessageCircle className="w-16 h-16 mb-3 opacity-30" />
                <p className="text-sm mb-1">Ask me anything!</p>
                <p className="text-xs">Type a question or use suggestions</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
