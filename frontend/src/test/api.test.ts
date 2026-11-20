import { describe, it, expect, vi, beforeEach } from "vitest";
import { api, ApiError } from "../services/api";

describe("Centralized API Client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("successfully calls getHealth and returns typed response", async () => {
    const mockHealth = { status: "healthy", version: "0.4.0", project: "Q-TRACE" };
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealth,
    } as Response);

    const res = await api.getHealth();
    expect(res).toEqual(mockHealth);
  });

  it("successfully handles getCases with pagination query parameters", async () => {
    const mockCases = {
      items: [{ id: "1", case_number: "QC-2026-001", title: "Claim Test", status: "OPEN" }],
      total: 1,
      page: 1,
      page_size: 20,
      has_next: false,
    };

    const fetchSpy = vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockCases,
    } as Response);

    const res = await api.getCases(1, 20);
    expect(res.total).toBe(1);
    expect(fetchSpy).toHaveBeenCalledWith("/api/v1/cases?page=1&page_size=20", expect.anything());
  });

  it("correctly unwraps structured APIErrorResponse on 409 conflict", async () => {
    const errorPayload = {
      error: {
        code: "INTEGRITY_VIOLATION",
        message: "A case with this number already exists.",
        details: {},
      },
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 409,
      statusText: "Conflict",
      json: async () => errorPayload,
    } as Response);

    await expect(
      api.createCase({ case_number: "QC-2026-DUP", title: "Duplicate" })
    ).rejects.toThrow(ApiError);
  });
});

