import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCalendarAlt } from "@fortawesome/free-solid-svg-icons";

interface IssueProps {
  title: string;
  number: number;
  created_at: number;
  comments_count: number;
  repository: {
    key: string;
    owner_key: string;
  };
}

export function IssueCard({ issue }: { issue: IssueProps }) {
  return (
    <div
      style={{
        padding: "16px",
        border: "1px solid #e5e7eb",
        borderRadius: "8px",
        transition: "background-color 0.2s",
        cursor: "pointer",
      }}
      onMouseEnter={(e) =>
        (e.currentTarget.style.backgroundColor = "#f9fafb")
      }
      onMouseLeave={(e) =>
        (e.currentTarget.style.backgroundColor = "transparent")
      }
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <div>
          <a
            href={`https://github.com/${issue.repository.owner_key}/${issue.repository.key}/issues/${issue.number}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontWeight: "bold",
              textDecoration: "underline dotted",
              color: "black",
            }}
          >
            {issue.title}
          </a>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ backgroundColor: "#e5e7eb", padding: "4px 8px", borderRadius: "16px" }}>
              #{issue.number}
            </span>
            <span>•</span>
            <a
              href={`https://github.com/${issue.repository.owner_key}/${issue.repository.key}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                textDecoration: "underline dotted",
                color: "black",
              }}
            >
              {issue.repository.owner_key}/{issue.repository.key}
            </a>
          </div>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
            color: "#6b7280",
          }}
        >
          <FontAwesomeIcon icon={faCalendarAlt} style={{ width: "16px", height: "16px" }} />
          {new Date(issue.created_at * 1000).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
}
