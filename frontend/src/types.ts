export type Shortlink = {
  id: number;
  short_code: string;
  short_url: string;
  url: string;
  click_count: number;
};

export type ShortlinkCreate = {
  url: string;
};

export type ShortlinkUpdate = {
  url?: string;
  short_code?: string;
};

export type HealthStatus = {
  ok: boolean;
};
