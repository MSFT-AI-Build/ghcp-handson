import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { calls, server, setNextStreamPlan } from "./server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  calls.length = 0;
  setNextStreamPlan(null);
  localStorage.clear();
});
afterAll(() => server.close());
