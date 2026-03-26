
import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import "jest-axe/extend-expect";
import ActionButton from "./ActionButton";

jest.mock("next/link", () => {
  return ({ children }: { children: React.ReactNode }) => children;
});

describe("ActionButton Accessibility", () => {

  it("should have no accessibility violations (button mode)", async () => {
    const { container } = render(
      <ActionButton onClick={() => {}} tooltipLabel="Click button">
        Click Me
      </ActionButton>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("should have no accessibility violations (link mode)", async () => {
    const { container } = render(
      <ActionButton url="https://example.com" tooltipLabel="Go to link">
        Visit
      </ActionButton>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

});