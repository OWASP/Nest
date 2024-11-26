import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";  
import '@testing-library/jest-dom'; 
import App from "../src/App";  

test("renders Home page heading and the contribute link", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );

  const contributeLinks = screen.getAllByText(/contribute/i);
  expect(contributeLinks.length).toBeGreaterThan(0);
  const firstContributeLink = contributeLinks[0];
  expect(firstContributeLink).toHaveAttribute('href', '/projects/contribute');
});