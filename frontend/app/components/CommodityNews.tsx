"use client";

import { useState } from "react";
import type { NewsArticle } from "../types";

interface CommodityNewsProps {
  articles: NewsArticle[];
}

export default function CommodityNews({ articles }: CommodityNewsProps) {
  const [expanded, setExpanded] = useState(false);

  if (articles.length === 0) return null;

  return (
    <div className="mt-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs text-text-muted hover:text-accent-blue transition-colors cursor-pointer"
      >
        <span
          className={`transition-transform duration-200 ${expanded ? "rotate-90" : ""}`}
        >
          &#9654;
        </span>
        {expanded ? "Hide" : "Show"} latest news
      </button>

      {expanded && (
        <div className="mt-2 space-y-2">
          {articles.map((article, idx) => (
            <a
              key={idx}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-md bg-navy-900/40 px-3 py-2 border border-navy-700/30 hover:border-accent-blue/40 transition-colors"
            >
              <p className="text-xs font-medium text-text-primary leading-snug line-clamp-2">
                {article.title}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] text-accent-cyan font-medium">
                  {article.source}
                </span>
                {article.published_at && (
                  <span className="text-[10px] text-text-muted">
                    {new Date(article.published_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                )}
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
