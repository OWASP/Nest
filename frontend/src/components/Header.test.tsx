import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import "jest-axe/extend-expect";
import Header from "./Header";

describe("Header Accessibility", () => {
  it("should have no accessibility violations", async () => {
    const { container } = render(<Header />);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });
});