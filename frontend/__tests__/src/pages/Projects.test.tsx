import React from "react";
import { render, screen } from "@testing-library/react";
import '@testing-library/jest-dom';
import Projects from "../../../src/pages/Projects";

describe("Projects Component", () => {
    test("renders the Projects component with the correct content", () => {

        render(<Projects />);
        const projectText = screen.getByText(/project page/i);
        expect(projectText).toBeInTheDocument();
    });
});
