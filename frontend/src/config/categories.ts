// Display text lives in i18n locale files under cat.<id>.*; ids match the backend.
export const CATEGORY_IDS = ["wet", "dry", "plastic", "metal", "reusable", "non_recyclable"] as const;
export type CategoryId = (typeof CATEGORY_IDS)[number];
export const isCategory = (v: string): v is CategoryId => (CATEGORY_IDS as readonly string[]).includes(v);
