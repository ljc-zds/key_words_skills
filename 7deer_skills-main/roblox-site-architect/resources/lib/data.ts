/**
 * data.ts — 数据访问层模板
 *
 * 复制此文件到你的项目 src/lib/data.ts
 * 然后替换以下内容：
 * - Item/Boss/Card → 你游戏的具体数据类型
 * - getItems() / getItemBySlug() → 你游戏的数据访问函数
 * - JSON 导入路径 → 你游戏的数据文件路径
 */

import itemsData from '@/data/items.json';
import configData from '@/data/game.config.json';

// ============================================================
// 类型定义 — 替换为你的游戏数据模型
// ============================================================

export interface Item {
  id: string;
  name: string;
  slug: string;
  category: string;           // e.g. "weapon" / "fruit" / "class"
  rarity?: string;            // e.g. "Legendary" / "Epic"
  description: string;
  tags: string[];
  // 替换为你的游戏特有字段
  // damage?: number;
  // health?: number;
  // cost?: number;
}

export interface GameConfig {
  game: {
    name: string;
    robloxId: string;
    developer: string;
    genre: string;
    currentVersion: string;
    lastUpdated: string;
    chapters?: number;
    platforms: string[];
  };
  stats: {
    visits: string;
    favorites: string;
    likes?: string;
    onlineNow?: string;
    serverSize: number;
    active: boolean;
  };
  seo: {
    siteTitle: string;
    siteDescription: string;
    baseUrl: string;
    primaryKeywords: string[];
    secondaryKeywords: string[];
    defaultOgImage: string;
  };
  routes: { path: string; title: string; priority: string }[];
}

// ============================================================
// 数据加载 — 替换为你的数据文件
// ============================================================

const items: Item[] = (itemsData as { items: Item[] }).items;
const config: GameConfig = configData as GameConfig;

// ============================================================
// 数据访问函数 — 替换为你的函数
// ============================================================

export function getItems(): Item[] {
  return items;
}

export function getItemBySlug(slug: string): Item | undefined {
  return items.find((item) => item.slug === slug);
}

export function getItemsByCategory(category: string): Item[] {
  return items.filter((item) => item.category === category);
}

export function getGameConfig(): GameConfig {
  return config;
}

export function getItemsByTag(tag: string): Item[] {
  return items.filter((item) => item.tags.includes(tag));
}
