import { fetcher, post } from "../client";

export type StatsigFlag = {
  id: number;
  key: string;
  key2: string;
  created_at: string;
};

export const getFeatureFlags = () =>
  fetcher<StatsigFlag[]>(
    "/v1/statsigfeatureflag",
  );

export const createFeatureFlag = (data: {
  key: string;
  key2: string;
}) =>
  post<StatsigFlag>(
    "/v1/statsigfeatureflag",
    data,
  );

export const triggerTestEvent = () =>
  post("/v1/trigger-events", {
    channel: "global",
    event_type: "message",
    payload: {
      message: "manual trigger",
      at: new Date().toISOString(),
    },
  });