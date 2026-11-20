import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Card, CardTitle } from "../components/ui/Card";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { EmptyState } from "../components/ui/EmptyState";

describe("Design System UI Components", () => {
  it("renders Button with proper label and handles click event", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Audit File</Button>);

    const btn = screen.getByRole("button", { name: /audit file/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("renders Button loading state correctly and disables button", () => {
    render(<Button isLoading>Process</Button>);
    const btn = screen.getByRole("button");
    expect(btn).toBeDisabled();
  });

  it("renders Badge variants with correct uppercase styling", () => {
    render(<Badge variant="verified">Verified Hash</Badge>);
    const badge = screen.getByText(/verified hash/i);
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("text-emerald-400");
  });

  it("renders Card container with title", () => {
    render(
      <Card>
        <CardTitle>Evidence Dossier</CardTitle>
        <p>Details here</p>
      </Card>
    );
    expect(screen.getByText("Evidence Dossier")).toBeInTheDocument();
    expect(screen.getByText("Details here")).toBeInTheDocument();
  });

  it("renders StatusIndicator with operational dot", () => {
    render(<StatusIndicator status="operational" label="ONLINE" />);
    expect(screen.getByText("ONLINE")).toBeInTheDocument();
  });

  it("renders EmptyState with custom title, description, and action", () => {
    render(
      <EmptyState
        title="No Cases Available"
        description="Please create your first case"
        action={<button>Create</button>}
      />
    );
    expect(screen.getByText("No Cases Available")).toBeInTheDocument();
    expect(screen.getByText("Please create your first case")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Create" })).toBeInTheDocument();
  });
});

