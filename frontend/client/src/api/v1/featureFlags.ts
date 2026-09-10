import { fetcher, post } from "../client";

export type StatsigFlag = {
  id: number;
  product: string;
  environment: string;
  last_checksum: string;
  created_at: string;
};

export type SnapshotRow = {
  id: number;
  productid: string;
  productName: string;
  timestamp: string;
  featureflaglastchecksum: string;
};

export type StatsigFeatureDetails = {
  id: number;
  environment: string;
  checksum: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
  snapshots: SnapshotRow[];
};

export const getFeatureFlags = () =>
  fetcher<StatsigFlag[]>(
    "/v1/statsigfeatureflag",
  );

export const getFeatureFlagByChecksum = (checksum: string) =>
  fetcher<StatsigFeatureDetails[]>(
    `/v1/statsigfeatureflag?checksum=${encodeURIComponent(checksum)}`,
  );

export const getSnapshotRows = (params: Record<string, string>) => {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value && value.trim() !== "") {
      query.set(key, value);
    }
  });

  const search = query.toString();
  return fetcher<SnapshotRow[]>(
    `/v1/productstatsigsnapshots${search ? `?${search}` : ""}`,
  );
};

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