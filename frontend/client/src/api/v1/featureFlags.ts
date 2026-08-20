import { fetcher, post } from "../client";

export type StatsigFlag = {
  id: number;
  product: string;
  environment: string;
  last_checksum: string;
  created_at: string;
};

export const getFeatureFlags = () =>
  fetcher<StatsigFlag[]>(
    "/v1/statsigfeatureflag",
  );

export const createFeatureFlag = (data: {
  product: string;
  environment: string;
  last_checksum: string;
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