import { fetcher } from "../client";

export const getFeatureFlags = () =>
  fetcher("/v2/statsigfeatureflag");
