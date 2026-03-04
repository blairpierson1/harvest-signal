"use client";

import type { NewsArticle } from "../types";

interface CommodityNewsProps {
  articles: NewsArticle[];
}

export default function CommodityNews({ articles }: CommodityNewsProps) {
  if (articles.length === 0) return null;

  return (
    <div className="mt-4">
      <span className="text-xs text-text-muted uppercase tracking-widest block mb-2">
        Latest News
      </span>
      <div className="space-y-2">
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
    </div>
  );
}
