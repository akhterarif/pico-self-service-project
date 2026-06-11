import React, { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createAiChat, listAiChats, type ChatMessage } from "../api";
import { Empty, ErrorBox, Spinner } from "../components/common";

export function AIChatPage() {
  const [prompt, setPrompt] = useState("");

  const {
    data: chats,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["ai-chats"],
    queryFn: listAiChats,
    refetchInterval: 5000,
  });

  const mutation = useMutation({
    mutationFn: createAiChat,
    onSuccess: () => {
      setPrompt("");
      refetch();
    },
  });

  const isThinking =
    mutation.isLoading || chats?.some((chat) => chat.status === "PENDING");

  return (
    <div className="space-y-6">
      <div className="rounded border border-line bg-white p-6">
        <h1 className="text-2xl font-semibold">AI Assist</h1>
        <p className="mt-2 text-sm text-slate-600">
          Use AI chat to get package, billing, and VM details from the database.
          New messages are processed asynchronously and stored for later review.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded border border-line bg-white p-6">
          <h2 className="text-lg font-semibold">Ask the AI</h2>
          <textarea
            className="mt-4 w-full rounded border border-line bg-slate-50 p-3 text-sm outline-none focus:border-brand"
            rows={5}
            placeholder="Ask about packages, invoices, or cloud resources."
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />
          <div className="mt-4 flex items-center gap-3">
            <button
              className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              disabled={!prompt.trim() || mutation.isLoading}
              onClick={() => mutation.mutate(prompt.trim())}
            >
              {mutation.isLoading ? "Thinking..." : "Send request"}
            </button>
            {isThinking && (
              <span className="text-sm text-slate-600">
                Processing chat requests...
              </span>
            )}
          </div>
          {mutation.isError && (
            <ErrorBox message="Failed to send chat request." />
          )}
        </section>

        <section className="rounded border border-line bg-white p-6">
          <h2 className="text-lg font-semibold">Status</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-600">
            <p>
              New chat requests will be processed by Celery in the background.
            </p>
            <p>
              This view refreshes every 5 seconds to show updated responses.
            </p>
            <p>{isThinking ? "The AI is thinking." : "No pending requests."}</p>
          </div>
        </section>
      </div>

      <section className="rounded border border-line bg-white p-6">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold">Recent AI Chats</h2>
          <span className="text-sm text-slate-500">
            Auto-refresh every 5 seconds
          </span>
        </div>
        {isLoading ? (
          <Spinner />
        ) : isError ? (
          <ErrorBox message="Unable to load chat history." />
        ) : !chats?.length ? (
          <Empty title="No chat history yet." />
        ) : (
          <div className="space-y-4">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className="rounded border border-slate-200 bg-slate-50 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-600">
                  <span>{new Date(chat.created_at).toLocaleString()}</span>
                  <span className="rounded-full bg-slate-200 px-3 py-1 text-xs uppercase tracking-wide text-slate-700">
                    {chat.status}
                  </span>
                </div>
                <div className="mt-4 space-y-3">
                  <div>
                    <div className="text-sm font-semibold">Prompt</div>
                    <p className="mt-1 text-sm text-slate-700">{chat.prompt}</p>
                  </div>
                  <div>
                    <div className="text-sm font-semibold">Response</div>
                    <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">
                      {chat.status === "PENDING"
                        ? "Thinking..."
                        : chat.response || "No response yet."}
                    </p>
                  </div>
                  {chat.error ? (
                    <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                      {chat.error}
                    </div>
                  ) : null}
                  {chat.source_docs?.length ? (
                    <div className="rounded border border-line bg-white p-3">
                      <div className="text-sm font-semibold">
                        Relevant data from Chroma
                      </div>
                      <ol className="mt-2 space-y-2 text-sm text-slate-700">
                        {chat.source_docs.map((doc, index) => (
                          <li
                            key={index}
                            className="rounded border border-slate-200 bg-slate-50 p-3"
                          >
                            <div className="text-xs text-slate-500">
                              Source {index + 1}
                            </div>
                            <div className="mt-1 whitespace-pre-wrap">
                              {doc.document}
                            </div>
                          </li>
                        ))}
                      </ol>
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
