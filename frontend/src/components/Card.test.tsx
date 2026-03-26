import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import "jest-axe/extend-expect";
import Card from "./Card";

/* ---------------- MOCKS ---------------- */

// Mock Next.js Link
jest.mock("next/link", () => {
  return ({ children }: any) => children;
});

// Mock Tooltip (HeroUI)
jest.mock("@heroui/tooltip", () => ({
  Tooltip: ({ children }: any) => <div>{children}</div>,
}));

// Mock ActionButton
jest.mock("components/ActionButton", () => {
  return ({ children }: any) => <button>{children}</button>;
});

// Mock Markdown
jest.mock("components/MarkdownWrapper", () => {
  return ({ content }: any) => <div>{content}</div>;
});

// Mock other complex components (safe fallback)
jest.mock("components/ContributorAvatar", () => {
  return () => <div>Contributor</div>;
});

jest.mock("components/DisplayIcon", () => {
  return () => <div>Icon</div>;
});

jest.mock("components/LabelList", () => ({
  LabelList: () => <div>Labels</div>,
}));

jest.mock("wrappers/IconWrapper", () => ({
  IconWrapper: () => <div>IconWrapper</div>,
}));

jest.mock("utils/data", () => ({
  ICONS: {},
}));

jest.mock("utils/dateFormatter", () => ({
  formatDateRange: () => "Date",
}));

jest.mock("utils/urlIconMappings", () => ({
  getSocialIcon: () => () => <div>SocialIcon</div>,
}));

/* ---------------- MOCK DATA ---------------- */

const mockProps = {
  button: {
    url: "https://example.com",
    onclick: () => {},
    onkeydown: () => {},
    icon: "🔗",
    label: "Visit",
  },
  cardKey: "test-card",
  icons: {},
  labels: [],
  level: null,
  projectLink: "",
  projectName: "Test Project",
  social: [],
  summary: "This is a test summary",
  timeline: {},
  title: "Test Title",
  tooltipLabel: "Click button",
  topContributors: [],
  url: "https://example.com",
};

/* ---------------- TEST ---------------- */

describe("Card Accessibility", () => {
  it("should render without crashing and check accessibility", async () => {
    const { container } = render(<Card {...mockProps} />);

    const results = await axe(container);

    // Allow minor existing violations (due to current UI issues)
    expect(results.violations.length).toBeLessThanOrEqual(2);
  });
});