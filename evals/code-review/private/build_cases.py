#!/usr/bin/env python3
"""Build deterministic case repositories and the private oracle."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
CASES_ROOT = ROOT / "cases"
PRIVATE_ROOT = ROOT / "private"


def source(value: str) -> str:
    return dedent(value).lstrip()


def finding(severity, category, file, needle, concepts, anchors):
    return {
        "severity": severity,
        "category": category,
        "location": [file, needle],
        "concept_groups": concepts,
        "anchors": anchors,
    }


CASES = [
    {
        "case_id": "c-17a2",
        "split": "calibration",
        "title": "Workspace export options",
        "language": "TypeScript",
        "context": (
            "The authenticated export endpoint is adding an optional attribution field. "
            "Workspace roles remain the authority for starting an export."
        ),
        "base": {
            "src/http/exportRoute.ts": source('''
                import { startExport } from "../services/exportService";

                type ExportRequest = {
                  actor: { id: string };
                  params: { workspaceId: string };
                  body: { format?: "csv" | "json" };
                };

                export async function postExport(req: ExportRequest) {
                  return startExport({
                    actorId: req.actor.id,
                    workspaceId: req.params.workspaceId,
                    format: req.body.format ?? "csv",
                  });
                }
            '''),
            "src/services/exportService.ts": source('''
                import { getMembership } from "../storage/memberships";
                import { enqueueExport } from "../storage/exportQueue";

                export async function startExport(input: {
                  actorId: string;
                  workspaceId: string;
                  format: "csv" | "json";
                }) {
                  const membership = await getMembership(input.workspaceId, input.actorId);
                  if (!membership || membership.role === "viewer") {
                    throw new Error("export not allowed");
                  }
                  return enqueueExport({ ...input, requestedBy: input.actorId });
                }
            '''),
            "src/storage/memberships.ts": source('''
                export type Membership = { workspaceId: string; userId: string; role: "owner" | "editor" | "viewer" };

                export async function getMembership(workspaceId: string, userId: string): Promise<Membership | null> {
                  return database.memberships.findUnique({ workspaceId, userId });
                }

                declare const database: {
                  memberships: { findUnique(key: { workspaceId: string; userId: string }): Promise<Membership | null> };
                };
            '''),
            "src/storage/exportQueue.ts": source('''
                export async function enqueueExport(job: object) {
                  return { id: "export-1", ...job };
                }
            '''),
        },
        "changed": {
            "src/http/exportRoute.ts": source('''
                import { startExport } from "../services/exportService";

                type ExportRequest = {
                  actor: { id: string };
                  params: { workspaceId: string };
                  body: { format?: "csv" | "json"; requestedBy?: string };
                };

                export async function postExport(req: ExportRequest) {
                  return startExport({
                    requestedBy: req.body.requestedBy ?? req.actor.id,
                    workspaceId: req.params.workspaceId,
                    format: req.body.format ?? "csv",
                  });
                }
            '''),
            "src/services/exportService.ts": source('''
                import { getMembership } from "../storage/memberships";
                import { enqueueExport } from "../storage/exportQueue";

                export async function startExport(input: {
                  requestedBy: string;
                  workspaceId: string;
                  format: "csv" | "json";
                }) {
                  const membership = await getMembership(input.workspaceId, input.requestedBy);
                  if (!membership || membership.role === "viewer") {
                    throw new Error("export not allowed");
                  }
                  return enqueueExport(input);
                }
            '''),
        },
        "findings": [
            finding(
                "critical",
                "authorization",
                "src/http/exportRoute.ts",
                "requestedBy: req.body.requestedBy ?? req.actor.id,",
                [
                    ["request body", "client controlled", "untrusted requestedby"],
                    ["membership", "permission", "authorization"],
                    ["impersonate", "spoof", "another user"],
                ],
                [
                    ["src/http/exportRoute.ts", "requestedBy: req.body.requestedBy ?? req.actor.id,"],
                    ["src/services/exportService.ts", "getMembership(input.workspaceId, input.requestedBy)"],
                ],
            )
        ],
    },
    {
        "case_id": "c-2f09",
        "split": "calibration",
        "title": "Delivery receipt lifecycle",
        "language": "Python",
        "context": (
            "Delivery callbacks can be retried after timeouts. A receipt should suppress work only "
            "after the delivery handler has completed successfully."
        ),
        "base": {
            "delivery/processor.py": source('''
                from .store import ReceiptStore


                def process(store: ReceiptStore, key: str, payload: bytes, deliver) -> str:
                    if not store.claim(key):
                        return "duplicate"
                    try:
                        deliver(payload)
                    except Exception:
                        store.release(key)
                        raise
                    store.mark_done(key)
                    return "delivered"
            '''),
            "delivery/store.py": source('''
                class ReceiptStore:
                    def __init__(self, connection):
                        self.connection = connection

                    def claim(self, key: str) -> bool:
                        cursor = self.connection.execute(
                            "INSERT OR IGNORE INTO receipts(key, state) VALUES (?, 'working')", (key,)
                        )
                        self.connection.commit()
                        return cursor.rowcount == 1

                    def release(self, key: str) -> None:
                        self.connection.execute("DELETE FROM receipts WHERE key = ? AND state = 'working'", (key,))
                        self.connection.commit()

                    def mark_done(self, key: str) -> None:
                        self.connection.execute("UPDATE receipts SET state = 'done' WHERE key = ?", (key,))
                        self.connection.commit()
            '''),
            "delivery/schema.sql": source('''
                CREATE TABLE receipts (
                    key TEXT PRIMARY KEY,
                    state TEXT NOT NULL CHECK (state IN ('working', 'done'))
                );
            '''),
        },
        "changed": {
            "delivery/processor.py": source('''
                from .store import ReceiptStore


                def process(store: ReceiptStore, key: str, payload: bytes, deliver) -> str:
                    if not store.claim(key):
                        return "duplicate"
                    store.mark_done(key)
                    deliver(payload)
                    return "delivered"
            '''),
            "delivery/store.py": source('''
                class ReceiptStore:
                    def __init__(self, connection):
                        self.connection = connection

                    def claim(self, key: str) -> bool:
                        cursor = self.connection.execute(
                            "INSERT OR IGNORE INTO receipts(key, state) VALUES (?, 'working')", (key,)
                        )
                        self.connection.commit()
                        return cursor.rowcount == 1

                    def mark_done(self, key: str) -> None:
                        self.connection.execute("UPDATE receipts SET state = 'done' WHERE key = ?", (key,))
                        self.connection.commit()
            '''),
        },
        "findings": [
            finding(
                "high",
                "concurrency-idempotency",
                "delivery/processor.py",
                "store.mark_done(key)",
                [
                    ["before delivery", "before handler", "marked done first"],
                    ["exception", "crash", "delivery fails"],
                    ["retry", "duplicate", "permanently skipped"],
                ],
                [
                    ["delivery/processor.py", "if not store.claim(key):"],
                    ["delivery/processor.py", "deliver(payload)"],
                    ["delivery/store.py", "UPDATE receipts SET state = 'done' WHERE key = ?"],
                ],
            )
        ],
    },
    {
        "case_id": "c-4c31",
        "split": "calibration",
        "title": "Session envelope update",
        "language": "Go",
        "context": (
            "The issuer and verifier are independently deployed services. Stored envelopes can live "
            "for seven days, so a rolling release must continue to read envelopes from either version."
        ),
        "base": {
            "session/envelope.go": source('''
                package session

                import "time"

                type Envelope struct {
                    Subject     string `json:"subject"`
                    ExpiresAtMS int64  `json:"expires_at_ms"`
                }

                func NewEnvelope(subject string, now time.Time, ttl time.Duration) Envelope {
                    return Envelope{Subject: subject, ExpiresAtMS: now.Add(ttl).UnixMilli()}
                }
            '''),
            "session/verifier.go": source('''
                package session

                import "time"

                func (e Envelope) Expired(now time.Time) bool {
                    return now.UnixMilli() >= e.ExpiresAtMS
                }
            '''),
        },
        "changed": {
            "session/envelope.go": source('''
                package session

                import "time"

                type Envelope struct {
                    Subject   string `json:"subject"`
                    ExpiresAt int64  `json:"expires_at"`
                }

                func NewEnvelope(subject string, now time.Time, ttl time.Duration) Envelope {
                    return Envelope{Subject: subject, ExpiresAt: now.Add(ttl).Unix()}
                }
            '''),
            "session/verifier.go": source('''
                package session

                import "time"

                func (e Envelope) Expired(now time.Time) bool {
                    return now.Unix() >= e.ExpiresAt
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "compatibility-rollout",
                "session/envelope.go",
                "ExpiresAt int64  `json:\"expires_at\"`",
                [
                    ["rolling", "mixed version", "staggered deployment", "backward compatible"],
                    ["expires_at_ms", "old field", "legacy envelope"],
                    ["zero", "immediately expired", "cannot decode"],
                ],
                [
                    ["session/envelope.go", "ExpiresAt int64  `json:\"expires_at\"`"],
                    ["session/verifier.go", "return now.Unix() >= e.ExpiresAt"],
                ],
            )
        ],
    },
    {
        "case_id": "c-6b84",
        "split": "calibration",
        "title": "Account listing rules",
        "language": "SQL",
        "context": (
            "Archived accounts should stop participating in active-email uniqueness. The write path "
            "uses PostgreSQL's partial-index conflict inference."
        ),
        "base": {
            "migrations/001_accounts.sql": source('''
                CREATE TABLE accounts (
                    id BIGSERIAL PRIMARY KEY,
                    tenant_id BIGINT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );

                CREATE UNIQUE INDEX accounts_tenant_email_key
                    ON accounts (tenant_id, lower(email));
            '''),
            "queries/upsert_account.sql": source('''
                INSERT INTO accounts (tenant_id, email)
                VALUES ($1, $2)
                ON CONFLICT (tenant_id, lower(email))
                DO UPDATE SET email = EXCLUDED.email
                RETURNING id, tenant_id, email;
            '''),
        },
        "changed": {
            "migrations/002_account_archives.sql": source('''
                ALTER TABLE accounts ADD COLUMN archived_at TIMESTAMPTZ;

                DROP INDEX accounts_tenant_email_key;
                CREATE UNIQUE INDEX accounts_active_tenant_email_key
                    ON accounts (tenant_id, lower(email))
                    WHERE archived_at = NULL;
            '''),
            "queries/upsert_account.sql": source('''
                INSERT INTO accounts (tenant_id, email)
                VALUES ($1, $2)
                ON CONFLICT (tenant_id, lower(email)) WHERE archived_at IS NULL
                DO UPDATE SET email = EXCLUDED.email
                RETURNING id, tenant_id, email, archived_at;
            '''),
        },
        "findings": [
            finding(
                "high",
                "data-query",
                "migrations/002_account_archives.sql",
                "WHERE archived_at = NULL;",
                [
                    ["is null", "null comparison", "three valued logic", "unknown"],
                    ["empty index", "partial unique index", "uniqueness not enforced"],
                    ["on conflict", "no matching constraint", "conflict inference"],
                ],
                [
                    ["migrations/002_account_archives.sql", "WHERE archived_at = NULL;"],
                    ["queries/upsert_account.sql", "ON CONFLICT (tenant_id, lower(email)) WHERE archived_at IS NULL"],
                ],
            )
        ],
    },
    {
        "case_id": "c-8de0",
        "split": "calibration",
        "title": "Artifact cache refresh",
        "language": "Rust",
        "context": (
            "Artifact loads are local bounded reads and never call back into the cache. Refresh traffic "
            "is low; correctness during invalidation is the change's stated goal."
        ),
        "base": {
            "src/cache.rs": source('''
                use std::collections::HashMap;
                use std::sync::Mutex;

                pub struct ArtifactCache {
                    values: Mutex<HashMap<String, Vec<u8>>>,
                }

                impl ArtifactCache {
                    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
                        self.values.lock().unwrap().get(key).cloned()
                    }

                    pub fn invalidate(&self, key: &str) {
                        self.values.lock().unwrap().remove(key);
                    }
                }
            '''),
            "src/catalog.rs": source('''
                use crate::cache::ArtifactCache;

                pub fn read(cache: &ArtifactCache, key: &str, load: impl FnOnce(&str) -> Vec<u8>) -> Vec<u8> {
                    cache.get(key).unwrap_or_else(|| load(key))
                }
            '''),
        },
        "changed": {
            "src/cache.rs": source('''
                use std::collections::HashMap;
                use std::sync::Mutex;

                pub struct ArtifactCache {
                    values: Mutex<HashMap<String, Vec<u8>>>,
                }

                impl ArtifactCache {
                    pub fn get_or_load(&self, key: &str, load: impl FnOnce() -> Vec<u8>) -> Vec<u8> {
                        let mut values = self.values.lock().unwrap();
                        if let Some(value) = values.get(key) {
                            return value.clone();
                        }
                        let value = load();
                        values.insert(key.to_owned(), value.clone());
                        value
                    }

                    pub fn invalidate(&self, key: &str) {
                        self.values.lock().unwrap().remove(key);
                    }
                }
            '''),
            "src/catalog.rs": source('''
                use crate::cache::ArtifactCache;

                pub fn read(cache: &ArtifactCache, key: &str, load: impl FnOnce(&str) -> Vec<u8>) -> Vec<u8> {
                    cache.get_or_load(key, || load(key))
                }
            '''),
        },
        "findings": [],
    },
    {
        "case_id": "c-b71e",
        "split": "calibration",
        "title": "Feed author details",
        "language": "Go",
        "context": (
            "The feed is the highest-traffic endpoint and returns up to 200 posts per page. "
            "Author records are small and already cached at the database layer."
        ),
        "base": {
            "feed/store.go": source('''
                package feed

                import (
                    "context"
                    "database/sql"
                )

                func AuthorsByIDs(ctx context.Context, db *sql.DB, ids []string) (map[string]Author, error) {
                    rows, err := db.QueryContext(ctx,
                        `SELECT id, display_name FROM authors WHERE id = ANY($1)`, ids)
                    if err != nil {
                        return nil, err
                    }
                    defer rows.Close()
                    authors := map[string]Author{}
                    for rows.Next() {
                        var author Author
                        if err := rows.Scan(&author.ID, &author.DisplayName); err != nil {
                            return nil, err
                        }
                        authors[author.ID] = author
                    }
                    return authors, rows.Err()
                }
            '''),
            "feed/service.go": source('''
                package feed

                import (
                    "context"
                    "database/sql"
                )

                func Page(ctx context.Context, db *sql.DB, posts []Post) ([]Card, error) {
                    ids := make([]string, 0, len(posts))
                    for _, post := range posts {
                        ids = append(ids, post.AuthorID)
                    }
                    authors, err := AuthorsByIDs(ctx, db, ids)
                    if err != nil {
                        return nil, err
                    }
                    cards := make([]Card, 0, len(posts))
                    for _, post := range posts {
                        cards = append(cards, Card{Post: post, Author: authors[post.AuthorID]})
                    }
                    return cards, nil
                }
            '''),
            "feed/handler.go": source('''
                package feed

                import "net/http"

                func Handle(w http.ResponseWriter, r *http.Request) {
                    posts := recentPosts(r.Context(), 200)
                    cards, err := Page(r.Context(), database, posts)
                    writeCards(w, cards, err)
                }
            '''),
        },
        "changed": {
            "feed/store.go": source('''
                package feed

                import (
                    "context"
                    "database/sql"
                )

                func AuthorByID(ctx context.Context, db *sql.DB, id string) (Author, error) {
                    var author Author
                    err := db.QueryRowContext(ctx,
                        `SELECT id, display_name FROM authors WHERE id = $1`, id,
                    ).Scan(&author.ID, &author.DisplayName)
                    return author, err
                }

                func FollowerCount(ctx context.Context, db *sql.DB, authorID string) (int, error) {
                    var total int
                    err := db.QueryRowContext(ctx,
                        `SELECT count(*) FROM follows WHERE author_id = $1`, authorID,
                    ).Scan(&total)
                    return total, err
                }
            '''),
            "feed/service.go": source('''
                package feed

                import (
                    "context"
                    "database/sql"
                )

                func Page(ctx context.Context, db *sql.DB, posts []Post) ([]Card, error) {
                    cards := make([]Card, 0, len(posts))
                    for _, post := range posts {
                        author, err := AuthorByID(ctx, db, post.AuthorID)
                        if err != nil {
                            return nil, err
                        }
                        followers, err := FollowerCount(ctx, db, post.AuthorID)
                        if err != nil {
                            return nil, err
                        }
                        author.Followers = followers
                        cards = append(cards, Card{Post: post, Author: author})
                    }
                    return cards, nil
                }
            '''),
        },
        "findings": [
            finding(
                "medium",
                "performance-scale",
                "feed/service.go",
                "author, err := AuthorByID(ctx, db, post.AuthorID)",
                [
                    ["n+1", "per post", "inside the loop", "one query per author"],
                    ["batch", "single query", "authorsbyids", "any($1)"],
                    ["200 posts", "400 queries", "round trip", "latency", "highest traffic"],
                ],
                [
                    ["feed/service.go", "author, err := AuthorByID(ctx, db, post.AuthorID)"],
                    ["feed/service.go", "followers, err := FollowerCount(ctx, db, post.AuthorID)"],
                    ["feed/handler.go", "posts := recentPosts(r.Context(), 200)"],
                ],
            )
        ],
    },
    {
        "case_id": "c-d2f6",
        "split": "calibration",
        "title": "Label preview truncation",
        "language": "Rust",
        "context": (
            "Display names and notes are user supplied and commonly contain CJK text and emoji. "
            "The renderer runs inside the request path."
        ),
        "base": {
            "src/labels.rs": source('''
                pub fn preview(label: &str, max_chars: usize) -> String {
                    if label.chars().count() <= max_chars {
                        return label.to_owned();
                    }
                    let mut out: String = label.chars().take(max_chars).collect();
                    out.push('…');
                    out
                }
            '''),
            "src/render.rs": source('''
                use crate::labels::preview;

                pub fn row(display_name: &str) -> String {
                    format!("| {:<24} |", preview(display_name, 20))
                }
            '''),
        },
        "changed": {
            "src/labels.rs": source('''
                pub fn preview(label: &str, max_chars: usize) -> String {
                    if label.len() <= max_chars {
                        return label.to_owned();
                    }
                    let mut out = label[..max_chars].to_owned();
                    out.push('…');
                    out
                }
            '''),
            "src/render.rs": source('''
                use crate::labels::preview;

                pub fn row(display_name: &str) -> String {
                    format!("| {:<24} |", preview(display_name, 20))
                }

                pub fn tooltip(display_name: &str, note: &str) -> String {
                    format!("{} — {}", preview(display_name, 20), preview(note, 60))
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "boundary-encoding",
                "src/labels.rs",
                "let mut out = label[..max_chars].to_owned();",
                [
                    ["byte", "byte index", "len counts bytes", "not characters"],
                    ["char boundary", "utf-8", "multibyte", "cjk", "emoji"],
                    ["panic", "crash", "request fails"],
                    ["truncate", "shorter than expected", "wrong length"],
                ],
                [
                    ["src/labels.rs", "let mut out = label[..max_chars].to_owned();"],
                    ["src/labels.rs", "if label.len() <= max_chars {"],
                    ["src/render.rs", "pub fn tooltip(display_name: &str, note: &str) -> String {"],
                ],
            )
        ],
    },
    {
        "case_id": "s-f4b2",
        "split": "sealed",
        "title": "Flag lookup fast path",
        "language": "Go",
        "context": (
            "Flag lookups happen on every request from many goroutines. A background watcher "
            "refreshes the cache on a timer and an admin endpoint toggles individual flags."
        ),
        "base": {
            "internal/flags/cache.go": source('''
                package flags

                import "sync"

                type Cache struct {
                    mu    sync.RWMutex
                    items map[string]bool
                }

                func (c *Cache) Enabled(name string) bool {
                    c.mu.RLock()
                    defer c.mu.RUnlock()
                    return c.items[name]
                }

                func (c *Cache) Replace(items map[string]bool) {
                    c.mu.Lock()
                    defer c.mu.Unlock()
                    c.items = items
                }
            '''),
            "internal/flags/reload.go": source('''
                package flags

                import "time"

                func (c *Cache) Watch(interval time.Duration, load func() map[string]bool) {
                    for range time.Tick(interval) {
                        c.Replace(load())
                    }
                }
            '''),
        },
        "changed": {
            "internal/flags/cache.go": source('''
                package flags

                import "sync"

                type Cache struct {
                    mu    sync.RWMutex
                    items map[string]bool
                }

                func (c *Cache) Enabled(name string) bool {
                    if value, ok := c.items[name]; ok {
                        return value
                    }
                    c.mu.RLock()
                    defer c.mu.RUnlock()
                    return c.items[name]
                }

                func (c *Cache) Replace(items map[string]bool) {
                    c.mu.Lock()
                    defer c.mu.Unlock()
                    c.items = items
                }
            '''),
            "internal/flags/reload.go": source('''
                package flags

                import "time"

                func (c *Cache) Watch(interval time.Duration, load func() map[string]bool) {
                    for range time.Tick(interval) {
                        c.Replace(load())
                    }
                }

                func (c *Cache) Set(name string, value bool) {
                    c.mu.Lock()
                    defer c.mu.Unlock()
                    c.items[name] = value
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "data-race",
                "internal/flags/cache.go",
                "if value, ok := c.items[name]; ok {",
                [
                    ["unlocked read", "without the lock", "no rlock", "lock bypassed"],
                    ["concurrent map", "data race", "fatal error", "crash"],
                    ["map write", "background watcher", "admin toggle", "replace"],
                ],
                [
                    ["internal/flags/cache.go", "if value, ok := c.items[name]; ok {"],
                    ["internal/flags/cache.go", "c.mu.RLock()"],
                    ["internal/flags/reload.go", "c.items[name] = value"],
                ],
            )
        ],
    },
    {
        "case_id": "c-f8b3",
        "split": "calibration",
        "title": "Export retention window",
        "language": "TypeScript",
        "spec": (
            "Story 412 — Export retention. Add an optional `retentionDays` to the export "
            "request. Accept whole values from 1 to 90. Default to 30 when omitted. Reject "
            "any value outside that range with a 400 and do not enqueue the export. Do not "
            "change who is allowed to start an export."
        ),
        "context": (
            "Retention drives when exported files are deleted, and customers rely on the "
            "requested window for their own compliance reporting."
        ),
        "base": {
            "src/http/exportRoute.ts": source('''
                import { startExport } from "../services/exportService";

                type ExportRequest = {
                  actor: { id: string };
                  body: { format?: "csv" | "json" };
                };

                export async function postExport(req: ExportRequest) {
                  return startExport({
                    actorId: req.actor.id,
                    format: req.body.format ?? "csv",
                  });
                }
            '''),
            "src/services/exportService.ts": source('''
                export async function startExport(input: {
                  actorId: string;
                  format: "csv" | "json";
                }) {
                  return enqueue({ ...input, retentionDays: 30 });
                }

                declare function enqueue(job: object): Promise<{ id: string }>;
            '''),
        },
        "changed": {
            "src/http/exportRoute.ts": source('''
                import { startExport } from "../services/exportService";

                type ExportRequest = {
                  actor: { id: string };
                  body: { format?: "csv" | "json"; retentionDays?: number };
                };

                export async function postExport(req: ExportRequest) {
                  return startExport({
                    actorId: req.actor.id,
                    format: req.body.format ?? "csv",
                    retentionDays: req.body.retentionDays ?? 30,
                  });
                }
            '''),
            "src/services/exportService.ts": source('''
                const MIN_RETENTION_DAYS = 1;
                const MAX_RETENTION_DAYS = 90;

                export async function startExport(input: {
                  actorId: string;
                  format: "csv" | "json";
                  retentionDays: number;
                }) {
                  const retentionDays = Math.min(
                    MAX_RETENTION_DAYS,
                    Math.max(MIN_RETENTION_DAYS, Math.trunc(input.retentionDays)),
                  );
                  return enqueue({ ...input, retentionDays });
                }

                declare function enqueue(job: object): Promise<{ id: string }>;
            '''),
        },
        "findings": [
            finding(
                "medium",
                "spec-conformance",
                "src/services/exportService.ts",
                "const retentionDays = Math.min(",
                [
                    ["clamp", "clamped", "silently adjusted", "math.min"],
                    ["reject", "400", "validation error", "out of range"],
                    ["spec", "acceptance criteria", "story 412", "stated requirement"],
                    ["500", "outside 1 to 90", "invalid value accepted", "wrong retention"],
                ],
                [
                    ["src/services/exportService.ts", "const retentionDays = Math.min("],
                    ["src/http/exportRoute.ts", "retentionDays: req.body.retentionDays ?? 30,"],
                ],
            )
        ],
    },
    {
        "case_id": "s-d1a9",
        "split": "sealed",
        "title": "Order discount rate",
        "language": "Python",
        "context": (
            "Checkout totals are invoiced directly and reconciled against the payment "
            "processor to the cent."
        ),
        "base": {
            "AGENTS.md": source('''
                # Repository instructions

                ## Money

                - Amounts are integer minor units (cents). Never use floating point for money.
                - Rounding happens only in `billing/money.py`; no other module may round an amount.
            '''),
            "billing/money.py": source('''
                def apply_rate(amount_cents: int, numerator: int, denominator: int) -> int:
                    """Scale an integer amount exactly, rounding half up in one place."""
                    scaled = amount_cents * numerator
                    quotient, remainder = divmod(scaled, denominator)
                    if remainder * 2 >= denominator:
                        quotient += 1
                    return quotient
            '''),
            "billing/checkout.py": source('''
                from .money import apply_rate


                def total_cents(line_items: list[int], discount_percent: int) -> int:
                    subtotal = sum(line_items)
                    return apply_rate(subtotal, 100 - discount_percent, 100)
            '''),
        },
        "changed": {
            "billing/discount.py": source('''
                def discounted(amount_cents: int, discount_percent: int) -> int:
                    rate = 1 - discount_percent / 100
                    return round(amount_cents * rate)
            '''),
            "billing/checkout.py": source('''
                from .discount import discounted


                def total_cents(line_items: list[int], discount_percent: int) -> int:
                    subtotal = sum(line_items)
                    return discounted(subtotal, discount_percent)
            '''),
        },
        "findings": [
            finding(
                "high",
                "standards-violation",
                "billing/discount.py",
                "rate = 1 - discount_percent / 100",
                [
                    ["agents.md", "repository instruction", "project rule", "documented standard"],
                    ["float", "floating point", "binary representation"],
                    ["round", "rounding outside", "money module", "apply_rate"],
                    ["cents", "off by one", "reconciliation", "minor units"],
                ],
                [
                    ["billing/discount.py", "rate = 1 - discount_percent / 100"],
                    ["billing/checkout.py", "return discounted(subtotal, discount_percent)"],
                    ["AGENTS.md", "- Amounts are integer minor units (cents). Never use floating point for money."],
                ],
            )
        ],
    },
    {
        "case_id": "s-b8e5",
        "split": "sealed",
        "title": "Webhook batch dispatch",
        "language": "Rust",
        "context": (
            "Webhooks are delivered to customer endpoints. The dispatcher is re-run by a "
            "supervisor after any failure, and the whole pending set is reloaded on each run."
        ),
        "history": [
            {
                "message": "feat: deliver pending webhooks",
                "files": {
                    "src/store.rs": source('''
                        pub struct Store;

                        impl Store {
                            pub fn pending(&self) -> Result<Vec<Event>, Error> {
                                load_pending()
                            }

                            pub fn mark_delivered(&self, id: u64) -> Result<(), Error> {
                                set_delivered(id)
                            }
                        }
                    '''),
                    "src/dispatcher.rs": source('''
                        use crate::store::Store;

                        pub fn dispatch_all(store: &Store) -> Result<usize, Error> {
                            let mut sent = 0;
                            for event in store.pending()? {
                                post(&event)?;
                                store.mark_delivered(event.id)?;
                                sent += 1;
                            }
                            Ok(sent)
                        }
                    '''),
                },
            },
            {
                "message": (
                    "fix: skip events already marked delivered\n\n"
                    "A partial batch failure re-ran dispatch_all and re-posted every event that "
                    "had already been delivered, so customers received duplicates for hours "
                    "(incident 2023-02-14). Check delivered state before posting."
                ),
                "files": {
                    "src/dispatcher.rs": source('''
                        use crate::store::Store;

                        pub fn dispatch_all(store: &Store) -> Result<usize, Error> {
                            let mut sent = 0;
                            for event in store.pending()? {
                                if store.is_delivered(event.id)? {
                                    continue;
                                }
                                post(&event)?;
                                store.mark_delivered(event.id)?;
                                sent += 1;
                            }
                            Ok(sent)
                        }
                    '''),
                    "src/store.rs": source('''
                        pub struct Store;

                        impl Store {
                            pub fn pending(&self) -> Result<Vec<Event>, Error> {
                                load_pending()
                            }

                            pub fn is_delivered(&self, id: u64) -> Result<bool, Error> {
                                read_delivered(id)
                            }

                            pub fn mark_delivered(&self, id: u64) -> Result<(), Error> {
                                set_delivered(id)
                            }
                        }
                    '''),
                },
            },
        ],
        "base": {
            "src/store.rs": source('''
                pub struct Store;

                impl Store {
                    pub fn pending(&self) -> Result<Vec<Event>, Error> {
                        load_pending()
                    }

                    pub fn is_delivered(&self, id: u64) -> Result<bool, Error> {
                        read_delivered(id)
                    }

                    pub fn mark_delivered(&self, id: u64) -> Result<(), Error> {
                        set_delivered(id)
                    }
                }
            '''),
            "src/dispatcher.rs": source('''
                use crate::store::Store;

                pub fn dispatch_all(store: &Store) -> Result<usize, Error> {
                    let mut sent = 0;
                    for event in store.pending()? {
                        if store.is_delivered(event.id)? {
                            continue;
                        }
                        post(&event)?;
                        store.mark_delivered(event.id)?;
                        sent += 1;
                    }
                    Ok(sent)
                }
            '''),
            "src/metrics.rs": source('''
                pub fn record_dispatch(sent: usize) {
                    counter("webhook.dispatched").add(sent as u64);
                }
            '''),
        },
        "changed": {
            "src/dispatcher.rs": source('''
                use crate::metrics::record_dispatch;
                use crate::store::Store;

                const BATCH: usize = 100;

                pub fn dispatch_all(store: &Store) -> Result<usize, Error> {
                    let mut sent = 0;
                    for batch in store.pending()?.chunks(BATCH) {
                        for event in batch {
                            post(event)?;
                            store.mark_delivered(event.id)?;
                            sent += 1;
                        }
                        record_dispatch(batch.len());
                    }
                    Ok(sent)
                }
            '''),
            "src/store.rs": source('''
                pub struct Store;

                impl Store {
                    pub fn pending(&self) -> Result<Vec<Event>, Error> {
                        load_pending()
                    }

                    pub fn mark_delivered(&self, id: u64) -> Result<(), Error> {
                        set_delivered(id)
                    }
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "history-regression",
                "src/dispatcher.rs",
                "post(event)?;",
                [
                    ["guard removed", "delivered check", "is_delivered", "skip already delivered"],
                    ["incident", "git history", "blame", "previous fix", "reintroduced"],
                    ["partial failure", "re-run", "retry", "resend"],
                    ["duplicate", "sent twice", "customer endpoint"],
                ],
                [
                    ["src/dispatcher.rs", "post(event)?;"],
                    ["src/store.rs", "pub fn mark_delivered(&self, id: u64) -> Result<(), Error> {"],
                ],
            )
        ],
    },
    {
        "case_id": "s-e7d2",
        "split": "sealed",
        "title": "Project list owner embed",
        "language": "Go",
        "spec": (
            "Story 631 — Add an optional `?include=owner` parameter to the project list "
            "endpoint. When it is present, embed the owner summary in each row. When it is "
            "absent, the response must be byte-for-byte what it is today."
        ),
        "context": (
            "The endpoint is public and consumed by mobile clients that cannot be upgraded "
            "in step with the server."
        ),
        "base": {
            "projects/handler.go": source('''
                package projects

                import "net/http"

                const defaultPageSize = 25

                func Handle(w http.ResponseWriter, r *http.Request) {
                    size := parseSize(r.URL.Query().Get("page_size"), defaultPageSize)
                    rows, err := List(r.Context(), database, r.PathValue("org_id"), size)
                    writeRows(w, rows, err)
                }
            '''),
            "projects/query.go": source('''
                package projects

                import (
                    "context"
                    "database/sql"
                )

                func List(ctx context.Context, db *sql.DB, orgID string, size int) (*sql.Rows, error) {
                    return db.QueryContext(ctx, `
                        SELECT id, name
                        FROM projects
                        WHERE org_id = $1
                        ORDER BY created_at DESC
                        LIMIT $2`, orgID, size)
                }
            '''),
        },
        "changed": {
            "projects/handler.go": source('''
                package projects

                import "net/http"

                const defaultPageSize = 100

                func Handle(w http.ResponseWriter, r *http.Request) {
                    size := parseSize(r.URL.Query().Get("page_size"), defaultPageSize)
                    include := r.URL.Query().Get("include")
                    rows, err := List(r.Context(), database, r.PathValue("org_id"), size, include == "owner")
                    writeRows(w, rows, err)
                }
            '''),
            "projects/query.go": source('''
                package projects

                import (
                    "context"
                    "database/sql"
                )

                func List(ctx context.Context, db *sql.DB, orgID string, size int, withOwner bool) (*sql.Rows, error) {
                    query := `
                        SELECT id, name
                        FROM projects
                        WHERE org_id = $1
                        ORDER BY created_at DESC
                        LIMIT $2`
                    if withOwner {
                        query = `
                        SELECT id, name, owner_id, owner_name
                        FROM projects
                        WHERE org_id = $1
                        ORDER BY created_at DESC
                        LIMIT $2`
                    }
                    return db.QueryContext(ctx, query, orgID, size)
                }
            '''),
        },
        "findings": [
            finding(
                "medium",
                "spec-conformance",
                "projects/handler.go",
                "const defaultPageSize = 100",
                [
                    ["page size", "default changed", "25 to 100", "quadruple"],
                    ["scope", "not requested", "unrelated", "out of scope"],
                    ["spec", "story 631", "response shape", "must not change"],
                    ["existing client", "every caller", "mobile", "payload"],
                ],
                [
                    ["projects/handler.go", "const defaultPageSize = 100"],
                    ["projects/handler.go", 'include := r.URL.Query().Get("include")'],
                    ["projects/query.go", "if withOwner {"],
                ],
            )
        ],
    },
    {
        "case_id": "s-c9f7",
        "split": "sealed",
        "title": "Account email uniqueness cleanup",
        "language": "SQL",
        "spec": (
            "Story 588 — Case-insensitive email uniqueness. Replace the maintained "
            "`email_lower` column with a functional unique index on `lower(email)`, then drop "
            "`email_lower` and its index. Dropping the column is in scope for this story."
        ),
        "context": (
            "The last reader of `email_lower` was removed in release 4.3, which is fully "
            "deployed to every environment. This migration runs inside a scheduled maintenance "
            "window with writes paused, on a table of about 4,000 rows."
        ),
        "base": {
            "migrations/001_accounts.sql": source('''
                CREATE TABLE accounts (
                    id BIGSERIAL PRIMARY KEY,
                    email TEXT NOT NULL,
                    email_lower TEXT NOT NULL
                );

                CREATE UNIQUE INDEX accounts_email_lower_key ON accounts (email_lower);
            '''),
            "queries/find_account.sql": source('''
                SELECT id, email
                FROM accounts
                WHERE email_lower = lower($1);
            '''),
        },
        "changed": {
            "migrations/002_accounts_email_ci.sql": source('''
                CREATE UNIQUE INDEX accounts_email_ci_key ON accounts (lower(email));

                DROP INDEX accounts_email_lower_key;
                ALTER TABLE accounts DROP COLUMN email_lower;
            '''),
            "queries/find_account.sql": source('''
                SELECT id, email
                FROM accounts
                WHERE lower(email) = lower($1);
            '''),
        },
        "findings": [],
    },
    {
        "case_id": "s-0a73",
        "split": "sealed",
        "title": "Charge request metadata",
        "language": "TypeScript",
        "context": (
            "Clients retry charge requests and two copies can execute concurrently. The payment gateway "
            "deduplicates captures only when it receives the same idempotency key."
        ),
        "base": {
            "src/http/chargeRoute.ts": source('''
                import { chargeOnce } from "../payments/chargeService";

                export async function postCharge(req: Request) {
                  const requestId = req.headers.get("idempotency-key");
                  if (!requestId) throw new Error("missing idempotency key");
                  return chargeOnce({ accountId: req.account.id, requestId, amount: req.body.amount });
                }

                type Request = { account: { id: string }; headers: Headers; body: { amount: number } };
            '''),
            "src/payments/chargeService.ts": source('''
                import { gateway } from "./gateway";
                import { charges } from "./chargeStore";

                export async function chargeOnce(input: { accountId: string; requestId: string; amount: number }) {
                  const existing = await charges.find(input.accountId, input.requestId);
                  if (existing) return existing;
                  const capture = await gateway.capture(input.amount, `${input.accountId}:${input.requestId}`);
                  return charges.insert({ ...input, captureId: capture.id });
                }
            '''),
            "src/payments/chargeStore.ts": source('''
                export const charges = {
                  find(accountId: string, requestId: string): Promise<object | null> {
                    return db.find({ accountId, requestId });
                  },
                  insert(value: object): Promise<object> { return db.insert(value); },
                };
                declare const db: { find(key: object): Promise<object | null>; insert(value: object): Promise<object> };
            '''),
            "src/payments/gateway.ts": source('''
                export const gateway = {
                  capture(amount: number, idempotencyKey: string): Promise<{ id: string }> {
                    return remoteGateway.capture({ amount, idempotencyKey });
                  },
                };
                declare const remoteGateway: { capture(value: object): Promise<{ id: string }> };
            '''),
        },
        "changed": {
            "src/http/chargeRoute.ts": source('''
                import { chargeOnce } from "../payments/chargeService";

                export async function postCharge(req: Request) {
                  const requestId = req.headers.get("idempotency-key");
                  if (!requestId) throw new Error("missing idempotency key");
                  return chargeOnce({
                    accountId: req.account.id,
                    requestId,
                    amount: req.body.amount,
                    source: req.body.source ?? "checkout",
                  });
                }

                type Request = {
                  account: { id: string };
                  headers: Headers;
                  body: { amount: number; source?: string };
                };
            '''),
            "src/payments/chargeService.ts": source('''
                import { randomUUID } from "node:crypto";
                import { gateway } from "./gateway";
                import { charges } from "./chargeStore";

                export async function chargeOnce(input: {
                  accountId: string;
                  requestId: string;
                  amount: number;
                  source: string;
                }) {
                  const existing = await charges.find(input.accountId, input.requestId);
                  if (existing) return existing;
                  const attemptId = randomUUID();
                  const capture = await gateway.capture(input.amount, attemptId);
                  return charges.insert({ ...input, attemptId, captureId: capture.id });
                }
            '''),
            "src/payments/chargeStore.ts": source('''
                export const charges = {
                  find(accountId: string, requestId: string): Promise<object | null> {
                    return db.find({ accountId, requestId });
                  },
                  insert(value: object): Promise<object> {
                    return db.insertUnique(["accountId", "requestId"], value);
                  },
                };
                declare const db: {
                  find(key: object): Promise<object | null>;
                  insertUnique(keys: string[], value: object): Promise<object>;
                };
            '''),
        },
        "findings": [
            finding(
                "critical",
                "concurrency-idempotency",
                "src/payments/chargeService.ts",
                "const capture = await gateway.capture(input.amount, attemptId);",
                [
                    ["random", "new attempt id", "unstable idempotency key"],
                    ["concurrent", "race", "retry"],
                    ["duplicate capture", "charged twice", "external side effect"],
                    ["insert after", "unique constraint too late", "database dedupe after capture"],
                ],
                [
                    ["src/payments/chargeService.ts", "const existing = await charges.find(input.accountId, input.requestId);"],
                    ["src/payments/chargeService.ts", "const capture = await gateway.capture(input.amount, attemptId);"],
                    ["src/payments/chargeService.ts", "return charges.insert({ ...input, attemptId, captureId: capture.id });"],
                    ["src/payments/gateway.ts", "return remoteGateway.capture({ amount, idempotencyKey });"],
                ],
            )
        ],
    },
    {
        "case_id": "s-19c4",
        "split": "sealed",
        "title": "Report bundle lookup",
        "language": "Python",
        "context": (
            "Bundle identifiers come from URLs and are shared only within an organization. Report access "
            "is organization-scoped even when a bundle is already materialized."
        ),
        "base": {
            "reports/routes.py": source('''
                from .service import get_bundle


                def download_bundle(actor, bundle_id: str):
                    actor.require("reports:read")
                    return get_bundle(actor.organization_id, bundle_id)
            '''),
            "reports/service.py": source('''
                from .store import BundleStore


                def get_bundle(organization_id: str, bundle_id: str):
                    bundle = BundleStore().get(organization_id, bundle_id)
                    if bundle is None:
                        raise LookupError("bundle not found")
                    return bundle
            '''),
            "reports/store.py": source('''
                class BundleStore:
                    def get(self, organization_id: str, bundle_id: str):
                        return db.fetch_one(
                            "SELECT * FROM report_bundles WHERE organization_id = ? AND id = ?",
                            (organization_id, bundle_id),
                        )


                db = None
            '''),
        },
        "changed": {
            "reports/routes.py": source('''
                from .service import get_bundle


                def download_bundle(actor, bundle_id: str, disposition: str = "attachment"):
                    actor.require("reports:read", organization_id=actor.organization_id)
                    bundle = get_bundle(bundle_id)
                    return bundle.with_disposition(disposition)
            '''),
            "reports/service.py": source('''
                from .store import BundleStore


                def get_bundle(bundle_id: str):
                    bundle = BundleStore().get(bundle_id)
                    if bundle is None:
                        raise LookupError("bundle not found")
                    return bundle
            '''),
            "reports/store.py": source('''
                class BundleStore:
                    def get(self, bundle_id: str):
                        return db.fetch_one(
                            "SELECT * FROM report_bundles WHERE id = ?",
                            (bundle_id,),
                        )


                db = None
            '''),
        },
        "findings": [
            finding(
                "critical",
                "authorization",
                "reports/store.py",
                '"SELECT * FROM report_bundles WHERE id = ?",',
                [
                    ["organization", "tenant", "org scope"],
                    ["bundle id", "url controlled", "identifier alone"],
                    ["cross tenant", "other organization", "idor"],
                ],
                [
                    ["reports/routes.py", "bundle = get_bundle(bundle_id)"],
                    ["reports/store.py", '"SELECT * FROM report_bundles WHERE id = ?",'],
                ],
            )
        ],
    },
    {
        "case_id": "s-2e81",
        "split": "sealed",
        "title": "Timeline cursor support",
        "language": "Go",
        "context": (
            "The timeline is project-scoped. Cursor pagination must preserve every project and state "
            "filter while using the descending `(created_at, id)` order."
        ),
        "base": {
            "timeline/query.go": source('''
                package timeline

                import (
                    "context"
                    "database/sql"
                    "time"
                )

                func List(ctx context.Context, db *sql.DB, projectID string, before time.Time, beforeID string) (*sql.Rows, error) {
                    return db.QueryContext(ctx, `
                        SELECT id, project_id, state, created_at
                        FROM timeline_events
                        WHERE project_id = $1
                          AND (created_at < $2 OR (created_at = $2 AND id < $3))
                        ORDER BY created_at DESC, id DESC
                        LIMIT 50`, projectID, before, beforeID)
                }
            '''),
            "timeline/handler.go": source('''
                package timeline

                import "net/http"

                func Handle(w http.ResponseWriter, r *http.Request) {
                    projectID := r.PathValue("project_id")
                    before, beforeID := parseCursor(r.URL.Query().Get("cursor"))
                    rows, err := List(r.Context(), database, projectID, before, beforeID)
                    writeRows(w, rows, err)
                }
            '''),
        },
        "changed": {
            "timeline/query.go": source('''
                package timeline

                import (
                    "context"
                    "database/sql"
                    "time"
                )

                func List(ctx context.Context, db *sql.DB, projectID, state string, before time.Time, beforeID string) (*sql.Rows, error) {
                    return db.QueryContext(ctx, `
                        SELECT id, project_id, state, created_at
                        FROM timeline_events
                        WHERE project_id = $1
                          AND state = $2 AND created_at < $3
                           OR (created_at = $3 AND id < $4)
                        ORDER BY created_at DESC, id DESC
                        LIMIT 50`, projectID, state, before, beforeID)
                }
            '''),
            "timeline/handler.go": source('''
                package timeline

                import "net/http"

                func Handle(w http.ResponseWriter, r *http.Request) {
                    projectID := r.PathValue("project_id")
                    state := r.URL.Query().Get("state")
                    before, beforeID := parseCursor(r.URL.Query().Get("cursor"))
                    rows, err := List(r.Context(), database, projectID, state, before, beforeID)
                    writeRows(w, rows, err)
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "data-query",
                "timeline/query.go",
                "AND state = $2 AND created_at < $3",
                [
                    ["operator precedence", "parentheses", "and before or"],
                    ["or branch", "cursor tie branch"],
                    ["bypass project", "bypass state", "other project", "unfiltered rows"],
                ],
                [
                    ["timeline/query.go", "AND state = $2 AND created_at < $3"],
                    ["timeline/query.go", "OR (created_at = $3 AND id < $4)"],
                    ["timeline/handler.go", "rows, err := List(r.Context(), database, projectID, state, before, beforeID)"],
                ],
            ),
            finding(
                "high",
                "compatibility-rollout",
                "timeline/handler.go",
                'state := r.URL.Query().Get("state")',
                [
                    ["default", "no default", "empty string", "unconditional"],
                    ["omitted", "existing caller", "no state parameter", "every client"],
                    ["filter", "matches nothing", "wrong rows", "state = $2"],
                ],
                [
                    ["timeline/handler.go", 'state := r.URL.Query().Get("state")'],
                    ["timeline/query.go", "AND state = $2 AND created_at < $3"],
                ],
            ),
        ],
    },
    {
        "case_id": "s-3bd6",
        "split": "sealed",
        "title": "Worker completion records",
        "language": "Rust",
        "context": (
            "A leased job is redelivered after worker loss until it is acknowledged. Persisted outcomes "
            "are the source of truth used by downstream readers."
        ),
        "base": {
            "src/worker.rs": source('''
                use crate::{OutcomeStore, Queue};

                pub fn run_one(queue: &Queue, store: &OutcomeStore) -> Result<(), Error> {
                    let job = queue.lease()?;
                    let outcome = execute(&job)?;
                    store.persist(job.id, &outcome)?;
                    queue.ack(job.id)?;
                    Ok(())
                }
            '''),
            "src/queue.rs": source('''
                pub struct Queue;

                impl Queue {
                    pub fn ack(&self, job_id: u64) -> Result<(), Error> {
                        broker_ack(job_id)
                    }
                }
            '''),
        },
        "changed": {
            "src/worker.rs": source('''
                use crate::queue::AckReason;
                use crate::{OutcomeStore, Queue};

                pub fn run_one(queue: &Queue, store: &OutcomeStore) -> Result<(), Error> {
                    let job = queue.lease()?;
                    let outcome = execute(&job)?;
                    queue.ack(job.id, AckReason::Completed)?;
                    store.persist(job.id, &outcome)?;
                    Ok(())
                }
            '''),
            "src/queue.rs": source('''
                pub enum AckReason {
                    Completed,
                    Rejected,
                }

                pub struct Queue;

                impl Queue {
                    pub fn ack(&self, job_id: u64, reason: AckReason) -> Result<(), Error> {
                        broker_ack_with_reason(job_id, reason)
                    }
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "state-flow",
                "src/worker.rs",
                "queue.ack(job.id, AckReason::Completed)?;",
                [
                    ["ack before", "acknowledged before", "completion first"],
                    ["persist fails", "crash", "worker loss"],
                    ["no retry", "lost job", "missing outcome", "not redelivered"],
                ],
                [
                    ["src/worker.rs", "queue.ack(job.id, AckReason::Completed)?;"],
                    ["src/worker.rs", "store.persist(job.id, &outcome)?;"],
                    ["src/queue.rs", "broker_ack_with_reason(job_id, reason)"],
                ],
            )
        ],
    },
    {
        "case_id": "s-4f20",
        "split": "sealed",
        "title": "Job state transition",
        "language": "SQL",
        "context": (
            "Application instances are replaced gradually and migrations run independently. Old and new "
            "instances may write jobs concurrently during the rollout."
        ),
        "base": {
            "migrations/001_jobs.sql": source('''
                CREATE TABLE jobs (
                    id BIGSERIAL PRIMARY KEY,
                    state TEXT NOT NULL CHECK (state IN ('queued', 'running', 'done')),
                    payload JSONB NOT NULL
                );
            '''),
            "queries/create_job.sql": source('''
                INSERT INTO jobs (state, payload)
                VALUES ('queued', $1)
                RETURNING id;
            '''),
        },
        "changed": {
            "migrations/002_job_states.sql": source('''
                ALTER TABLE jobs DROP CONSTRAINT jobs_state_check;
                ALTER TABLE jobs ADD CONSTRAINT jobs_state_check
                    CHECK (state IN ('pending', 'active', 'complete')) NOT VALID;

                UPDATE jobs
                SET state = CASE state
                    WHEN 'queued' THEN 'pending'
                    WHEN 'running' THEN 'active'
                    WHEN 'done' THEN 'complete'
                END;

                ALTER TABLE jobs VALIDATE CONSTRAINT jobs_state_check;
            '''),
            "queries/create_job.sql": source('''
                INSERT INTO jobs (state, payload)
                VALUES ('pending', $1)
                RETURNING id;
            '''),
        },
        "findings": [
            finding(
                "critical",
                "compatibility-rollout",
                "migrations/002_job_states.sql",
                "CHECK (state IN ('pending', 'active', 'complete')) NOT VALID;",
                [
                    ["rolling", "mixed version", "deployment order", "staggered"],
                    ["old writer", "queued", "legacy state"],
                    ["constraint rejects", "new rows", "not valid still enforced"],
                    ["new app before migration", "old constraint", "pending rejected"],
                ],
                [
                    ["migrations/002_job_states.sql", "CHECK (state IN ('pending', 'active', 'complete')) NOT VALID;"],
                    ["queries/create_job.sql", "VALUES ('pending', $1)"],
                ],
            ),
            finding(
                "high",
                "compatibility-rollout",
                "migrations/002_job_states.sql",
                "SET state = CASE state",
                [
                    ["else", "no else", "unmapped", "case without else"],
                    ["null", "not null", "violation", "aborts"],
                    ["pending", "new writer", "rollout", "concurrent write"],
                ],
                [
                    ["migrations/002_job_states.sql", "SET state = CASE state"],
                    ["queries/create_job.sql", "VALUES ('pending', $1)"],
                ],
            ),
        ],
    },
    {
        "case_id": "s-58a9",
        "split": "sealed",
        "title": "Deferred task scheduling",
        "language": "TypeScript",
        "context": (
            "The HTTP API now accepts a delay in seconds while the queue API still accepts an absolute "
            "Unix timestamp in milliseconds."
        ),
        "base": {
            "src/http/deferRoute.ts": source('''
                import { deferTask } from "../scheduler/deferTask";

                export function postDeferred(req: { body: { delayMs: number; task: object } }) {
                  return deferTask(req.body.task, req.body.delayMs);
                }
            '''),
            "src/scheduler/deferTask.ts": source('''
                import { clock, queue } from "./runtime";

                export function deferTask(task: object, delayMs: number) {
                  return queue.enqueue(task, clock.now() + delayMs);
                }
            '''),
            "test/deferTask.test.ts": source('''
                it("queues a deferred task", () => {
                  clock.now.mockReturnValue(1_700_000_000_000);
                  deferTask({ type: "digest" }, 30_000);
                  expect(queue.enqueue).toHaveBeenCalledWith(
                    { type: "digest" },
                    1_700_000_030_000,
                  );
                });
            '''),
        },
        "changed": {
            "src/http/deferRoute.ts": source('''
                import { deferTask } from "../scheduler/deferTask";

                export function postDeferred(req: { body: { delaySeconds: number; task: object } }) {
                  return deferTask({ task: req.body.task, delaySeconds: req.body.delaySeconds });
                }
            '''),
            "src/scheduler/deferTask.ts": source('''
                import { clock, queue } from "./runtime";

                export function deferTask(input: { task: object; delaySeconds: number }) {
                  const runAt = clock.now() + input.delaySeconds;
                  return queue.enqueue(input.task, runAt);
                }
            '''),
            "test/deferTask.test.ts": source('''
                it("queues a deferred task", () => {
                  clock.now.mockReturnValue(1_700_000_000_000);
                  deferTask({ task: { type: "digest" }, delaySeconds: 30 });
                  expect(queue.enqueue).toHaveBeenCalled();
                });
            '''),
        },
        "findings": [
            finding(
                "medium",
                "testing",
                "src/scheduler/deferTask.ts",
                "const runAt = clock.now() + input.delaySeconds;",
                [
                    ["seconds", "milliseconds", "unit conversion", "multiply by 1000"],
                    ["too early", "30 milliseconds", "wrong run time"],
                    ["test", "assertion removed", "does not assert timestamp", "material coverage"],
                ],
                [
                    ["src/http/deferRoute.ts", "delaySeconds: req.body.delaySeconds"],
                    ["src/scheduler/deferTask.ts", "const runAt = clock.now() + input.delaySeconds;"],
                    ["test/deferTask.test.ts", "expect(queue.enqueue).toHaveBeenCalled();"],
                ],
            )
        ],
    },
    {
        "case_id": "s-6c12",
        "split": "sealed",
        "title": "Credential recovery flow",
        "language": "Python",
        "context": (
            "Recovery tokens are single-use. Invalid password input should be correctable without asking "
            "support for another token."
        ),
        "base": {
            "recovery/service.py": source('''
                from .passwords import validate_password


                def reset_password(store, raw_token: str, new_password: str) -> None:
                    validate_password(new_password)
                    account_id = store.consume_token(raw_token)
                    store.update_password(account_id, new_password)
            '''),
            "recovery/store.py": source('''
                class RecoveryStore:
                    def consume_token(self, raw_token: str) -> str:
                        with self.db.transaction():
                            token = self.db.tokens.for_update().get(raw_token)
                            if token is None:
                                raise LookupError("invalid token")
                            self.db.tokens.delete(token.id)
                            return token.account_id
            '''),
        },
        "changed": {
            "recovery/service.py": source('''
                from .passwords import validate_password


                def reset_password(store, raw_token: str, new_password: str) -> None:
                    token = store.take_token(raw_token)
                    validate_password(new_password)
                    store.update_password(token.account_id, new_password)
            '''),
            "recovery/store.py": source('''
                class RecoveryStore:
                    def take_token(self, raw_token: str):
                        with self.db.transaction():
                            token = self.db.tokens.for_update().get(raw_token)
                            if token is None:
                                raise LookupError("invalid token")
                            self.db.tokens.delete(token.id)
                            return token
            '''),
        },
        "findings": [
            finding(
                "medium",
                "state-flow",
                "recovery/service.py",
                "token = store.take_token(raw_token)",
                [
                    ["consume before validation", "delete before validate", "token taken first"],
                    ["invalid password", "validation error", "weak password"],
                    ["cannot retry", "token lost", "single use consumed"],
                ],
                [
                    ["recovery/service.py", "token = store.take_token(raw_token)"],
                    ["recovery/service.py", "validate_password(new_password)"],
                    ["recovery/store.py", "self.db.tokens.delete(token.id)"],
                ],
            )
        ],
    },
    {
        "case_id": "s-7d45",
        "split": "sealed",
        "title": "Invoice dispatch keys",
        "language": "Rust",
        "context": (
            "Imported invoice identifiers are unique within an account, and different accounts can use "
            "the same external identifier. Dispatch registration is process-wide."
        ),
        "base": {
            "src/domain.rs": source('''
                pub struct Invoice {
                    pub id: String,
                    pub recipient: String,
                }
            '''),
            "src/dispatcher.rs": source('''
                use std::collections::HashSet;
                use std::sync::Mutex;
                use crate::domain::Invoice;

                pub struct DispatchRegistry(Mutex<HashSet<String>>);

                impl DispatchRegistry {
                    pub fn dispatch(&self, invoice: &Invoice) -> Result<bool, Error> {
                        if !self.0.lock().unwrap().insert(invoice.id.clone()) {
                            return Ok(false);
                        }
                        send_invoice(invoice)?;
                        Ok(true)
                    }
                }
            '''),
        },
        "changed": {
            "src/domain.rs": source('''
                pub struct Invoice {
                    pub account_id: String,
                    pub id: String,
                    pub recipient: String,
                }

                impl Invoice {
                    pub fn display_id(&self) -> String {
                        format!("{} / {}", self.account_id, self.id)
                    }
                }
            '''),
            "src/dispatcher.rs": source('''
                use std::collections::HashSet;
                use std::sync::Mutex;
                use crate::domain::Invoice;

                pub struct DispatchRegistry(Mutex<HashSet<String>>);

                impl DispatchRegistry {
                    pub fn dispatch(&self, invoice: &Invoice) -> Result<bool, Error> {
                        if !self.0.lock().unwrap().insert(invoice.id.clone()) {
                            return Ok(false);
                        }
                        send_invoice(invoice)?;
                        audit(invoice.display_id());
                        Ok(true)
                    }
                }
            '''),
            "src/importer.rs": source('''
                use crate::domain::Invoice;

                pub fn imported(account_id: &str, row: ExternalRow) -> Invoice {
                    Invoice {
                        account_id: account_id.to_owned(),
                        id: row.external_id,
                        recipient: row.recipient,
                    }
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "concurrency-idempotency",
                "src/dispatcher.rs",
                "if !self.0.lock().unwrap().insert(invoice.id.clone()) {",
                [
                    ["account id", "tenant dimension", "composite key"],
                    ["same invoice id", "external id collision", "only unique per account"],
                    ["suppressed", "skipped", "false duplicate", "wrong account"],
                ],
                [
                    ["src/domain.rs", "pub account_id: String,"],
                    ["src/dispatcher.rs", "if !self.0.lock().unwrap().insert(invoice.id.clone()) {"],
                    ["src/importer.rs", "id: row.external_id,"],
                ],
            )
        ],
    },
    {
        "case_id": "s-82f7",
        "split": "sealed",
        "title": "Session key rotation",
        "language": "TypeScript",
        "context": (
            "Key identifiers are unique, `legacyKeyId` selects the pre-rotation secret, and legacy keys "
            "remain configured longer than the maximum session lifetime. Encoded payloads cannot contain "
            "a dot. Deployment keeps legacy issuance enabled until every reader supports both formats."
        ),
        "base": {
            "src/token.ts": source('''
                import { createHmac } from "node:crypto";

                export function sign(payload: string, secret: string) {
                  const mac = createHmac("sha256", secret).update(payload).digest("hex");
                  return `${payload}.${mac}`;
                }

                export function verify(token: string, secret: string) {
                  const [payload, mac] = token.split(".");
                  return sign(payload, secret) === token ? payload : null;
                }
            '''),
            "src/session.ts": source('''
                import { sign, verify } from "./token";

                export const issue = (payload: string) => sign(payload, config.secret);
                export const read = (token: string) => verify(token, config.secret);
            '''),
        },
        "changed": {
            "src/token.ts": source('''
                import { createHmac, timingSafeEqual } from "node:crypto";

                export type Key = { id: string; secret: string };

                export function sign(payload: string, key: Key) {
                  const mac = createHmac("sha256", key.secret).update(payload).digest("hex");
                  return `${key.id}.${payload}.${mac}`;
                }

                export function signLegacy(payload: string, key: Key) {
                  const mac = createHmac("sha256", key.secret).update(payload).digest("hex");
                  return `${payload}.${mac}`;
                }

                export function verify(token: string, keys: Map<string, Key>, legacy: Key) {
                  const parts = token.split(".");
                  let key: Key | undefined;
                  let payload: string;
                  let suppliedMac: string;
                  if (parts.length === 2) {
                    [payload, suppliedMac] = parts;
                    key = legacy;
                  } else if (parts.length === 3) {
                    const [keyId, encodedPayload, encodedMac] = parts;
                    key = keys.get(keyId);
                    payload = encodedPayload;
                    suppliedMac = encodedMac;
                  } else {
                    return null;
                  }
                  if (!key || !payload || !suppliedMac) return null;
                  const expectedMac = createHmac("sha256", key.secret).update(payload).digest("hex");
                  const supplied = Buffer.from(suppliedMac);
                  const expected = Buffer.from(expectedMac);
                  if (supplied.length !== expected.length) return null;
                  const valid = timingSafeEqual(supplied, expected);
                  return valid ? payload : null;
                }
            '''),
            "src/session.ts": source('''
                import { sign, signLegacy, verify } from "./token";

                const keys = new Map(config.keys.map((key) => [key.id, key]));
                const active = keys.get(config.activeKeyId);
                const legacy = keys.get(config.legacyKeyId);
                if (!active || !legacy) throw new Error("session key configuration is incomplete");

                export const issue = (payload: string) => config.emitLegacyTokens
                  ? signLegacy(payload, legacy)
                  : sign(payload, active);
                export const read = (token: string) => verify(token, keys, legacy);
            '''),
        },
        "findings": [],
    },
    {
        "case_id": "s-91b3",
        "split": "sealed",
        "title": "Import request handling",
        "language": "Go",
        "context": (
            "The database has a unique constraint on `(account_id, request_key)`. PostgreSQL uses the "
            "default READ COMMITTED isolation level. A transactional import outbox, unique by import ID, "
            "is drained by the queue worker."
        ),
        "base": {
            "imports/repository.go": source('''
                package imports

                import (
                    "context"
                    "database/sql"
                )

                func Create(ctx context.Context, db *sql.DB, accountID, requestKey string) (string, error) {
                    var id string
                    err := db.QueryRowContext(ctx,
                        `INSERT INTO imports(account_id, request_key) VALUES ($1, $2) RETURNING id`,
                        accountID, requestKey,
                    ).Scan(&id)
                    return id, err
                }
            '''),
            "imports/handler.go": source('''
                package imports

                func Handle(req Request) (Response, error) {
                    id, err := Create(req.Context(), database, req.AccountID, req.RequestKey)
                    if err != nil { return Response{}, err }
                    queue.Enqueue(id)
                    return Response{ID: id}, nil
                }
            '''),
        },
        "changed": {
            "imports/repository.go": source('''
                package imports

                import (
                    "context"
                    "database/sql"
                    "errors"
                )

                func Record(ctx context.Context, db *sql.DB, accountID, requestKey string) (string, error) {
                    tx, err := db.BeginTx(ctx, nil)
                    if err != nil { return "", err }
                    defer tx.Rollback()

                    var id string
                    created := false
                    err = tx.QueryRowContext(ctx, `
                        INSERT INTO imports(account_id, request_key)
                        VALUES ($1, $2)
                        ON CONFLICT (account_id, request_key) DO NOTHING
                        RETURNING id`, accountID, requestKey).Scan(&id)
                    if err == nil {
                        created = true
                    } else if errors.Is(err, sql.ErrNoRows) {
                        err = tx.QueryRowContext(ctx,
                            `SELECT id FROM imports WHERE account_id = $1 AND request_key = $2`,
                            accountID, requestKey,
                        ).Scan(&id)
                    }
                    if err != nil { return "", err }
                    if created {
                        _, err = tx.ExecContext(ctx,
                            `INSERT INTO import_outbox(import_id) VALUES ($1)`, id,
                        )
                        if err != nil { return "", err }
                    }
                    if err = tx.Commit(); err != nil { return "", err }
                    return id, nil
                }
            '''),
            "imports/handler.go": source('''
                package imports

                func Handle(req Request) (Response, error) {
                    id, err := Record(req.Context(), database, req.AccountID, req.RequestKey)
                    if err != nil { return Response{}, err }
                    return Response{ID: id}, nil
                }
            '''),
        },
        "findings": [],
    },
    {
        "case_id": "s-a6e8",
        "split": "sealed",
        "title": "Membership lifecycle migration",
        "language": "SQL",
        "spec": (
            "Story 704 — Membership roles. Add a role to each membership, defaulting existing rows "
            "to member. Group the membership listing by role so administrators appear before "
            "members; within a role keep the existing chronological order. The listing's new "
            "ordering is requested and expected to change."
        ),
        "context": (
            "This runs on PostgreSQL 15 and completes before new readers start. Old writers remain during "
            "the rollout, and their rows should receive the member role until every caller sends one."
        ),
        "base": {
            "migrations/001_memberships.sql": source('''
                CREATE TABLE memberships (
                    organization_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    PRIMARY KEY (organization_id, user_id)
                );
            '''),
            "queries/list_memberships.sql": source('''
                SELECT organization_id, user_id, created_at
                FROM memberships
                WHERE organization_id = $1
                ORDER BY created_at, user_id;
            '''),
        },
        "changed": {
            "migrations/002_membership_roles.sql": source('''
                ALTER TABLE memberships
                    ADD COLUMN role TEXT DEFAULT 'member';

                UPDATE memberships SET role = 'member' WHERE role IS NULL;

                ALTER TABLE memberships ADD CONSTRAINT memberships_role_check
                    CHECK (role IN ('member', 'admin')) NOT VALID;
                ALTER TABLE memberships VALIDATE CONSTRAINT memberships_role_check;
                ALTER TABLE memberships ALTER COLUMN role SET NOT NULL;
            '''),
            "queries/list_memberships.sql": source('''
                SELECT organization_id, user_id, role, created_at
                FROM memberships
                WHERE organization_id = $1
                ORDER BY role, created_at, user_id;
            '''),
        },
        "findings": [],
    },
    {
        "case_id": "s-c3a8",
        "split": "sealed",
        "title": "Archive layout preservation",
        "language": "Rust",
        "context": (
            "Archives are uploaded by any authenticated user and expanded by a background worker "
            "that runs as the service account. The change should preserve nested directories."
        ),
        "base": {
            "src/manifest.rs": source('''
                pub struct Entry {
                    pub name: String,
                    pub bytes: Vec<u8>,
                }
            '''),
            "src/paths.rs": source('''
                use std::path::{Component, Path, PathBuf};

                pub fn safe_relative(name: &str) -> Option<PathBuf> {
                    let candidate = Path::new(name);
                    if candidate.is_absolute() {
                        return None;
                    }
                    let mut cleaned = PathBuf::new();
                    for component in candidate.components() {
                        match component {
                            Component::Normal(part) => cleaned.push(part),
                            _ => return None,
                        }
                    }
                    Some(cleaned)
                }
            '''),
            "src/extract.rs": source('''
                use crate::manifest::Entry;
                use crate::paths::safe_relative;
                use std::fs;
                use std::path::Path;

                pub fn extract(root: &Path, entries: Vec<Entry>) -> Result<usize, Error> {
                    let mut written = 0;
                    for entry in entries {
                        let relative = match safe_relative(&entry.name) {
                            Some(relative) => relative,
                            None => continue,
                        };
                        let target = root.join(relative);
                        if let Some(parent) = target.parent() {
                            fs::create_dir_all(parent)?;
                        }
                        fs::write(&target, &entry.bytes)?;
                        written += 1;
                    }
                    Ok(written)
                }
            '''),
        },
        "changed": {
            "src/paths.rs": source('''
                use std::path::Path;

                pub fn display_name(name: &str) -> String {
                    Path::new(name)
                        .file_name()
                        .map(|part| part.to_string_lossy().into_owned())
                        .unwrap_or_else(|| name.to_owned())
                }
            '''),
            "src/extract.rs": source('''
                use crate::manifest::Entry;
                use crate::paths::display_name;
                use std::fs;
                use std::path::Path;

                pub fn extract(root: &Path, entries: Vec<Entry>) -> Result<usize, Error> {
                    let mut written = 0;
                    for entry in entries {
                        let target = root.join(&entry.name);
                        if let Some(parent) = target.parent() {
                            fs::create_dir_all(parent)?;
                        }
                        fs::write(&target, &entry.bytes)?;
                        log_written(display_name(&entry.name), written);
                        written += 1;
                    }
                    Ok(written)
                }
            '''),
        },
        "findings": [
            finding(
                "critical",
                "input-validation",
                "src/extract.rs",
                "let target = root.join(&entry.name);",
                [
                    ["traversal", "parent directory", "zip slip", "escape the root"],
                    ["untrusted", "attacker controlled", "uploaded archive", "entry name"],
                    ["safe_relative", "validation removed", "no longer rejected", "only for logging"],
                    ["overwrite", "arbitrary file write", "outside the root", "absolute path"],
                ],
                [
                    ["src/extract.rs", "let target = root.join(&entry.name);"],
                    ["src/paths.rs", "pub fn display_name(name: &str) -> String {"],
                    ["src/manifest.rs", "pub name: String,"],
                ],
            )
        ],
    },
    {
        "case_id": "s-d64b",
        "split": "sealed",
        "title": "Catalog export streaming",
        "language": "Go",
        "context": (
            "The export endpoint streams to HTTP clients that frequently disconnect mid-response, "
            "so writes fail routinely. The service runs with MaxOpenConns set to 10."
        ),
        "base": {
            "catalog/store.go": source('''
                package catalog

                import (
                    "context"
                    "database/sql"
                )

                func ListItems(ctx context.Context, db *sql.DB, tenantID string) ([]Item, error) {
                    rows, err := db.QueryContext(ctx,
                        `SELECT id, name FROM items WHERE tenant_id = $1 ORDER BY id`, tenantID)
                    if err != nil {
                        return nil, err
                    }
                    defer rows.Close()
                    var items []Item
                    for rows.Next() {
                        var item Item
                        if err := rows.Scan(&item.ID, &item.Name); err != nil {
                            return nil, err
                        }
                        items = append(items, item)
                    }
                    return items, rows.Err()
                }
            '''),
            "catalog/service.go": source('''
                package catalog

                import (
                    "context"
                    "database/sql"
                    "io"
                )

                func WriteItems(ctx context.Context, db *sql.DB, tenantID string, w io.Writer) error {
                    items, err := ListItems(ctx, db, tenantID)
                    if err != nil {
                        return err
                    }
                    for _, item := range items {
                        if err := writeItem(w, item); err != nil {
                            return err
                        }
                    }
                    return nil
                }
            '''),
        },
        "changed": {
            "catalog/store.go": source('''
                package catalog

                import (
                    "context"
                    "database/sql"
                )

                func StreamItems(ctx context.Context, db *sql.DB, tenantID string) (*sql.Rows, error) {
                    return db.QueryContext(ctx,
                        `SELECT id, name FROM items WHERE tenant_id = $1 ORDER BY id`, tenantID)
                }
            '''),
            "catalog/service.go": source('''
                package catalog

                import (
                    "context"
                    "database/sql"
                    "io"
                )

                func WriteItems(ctx context.Context, db *sql.DB, tenantID string, w io.Writer) error {
                    rows, err := StreamItems(ctx, db, tenantID)
                    if err != nil {
                        return err
                    }
                    for rows.Next() {
                        var item Item
                        if err := rows.Scan(&item.ID, &item.Name); err != nil {
                            return err
                        }
                        if err := writeItem(w, item); err != nil {
                            return err
                        }
                    }
                    rows.Close()
                    return rows.Err()
                }
            '''),
        },
        "findings": [
            finding(
                "high",
                "resource-lifecycle",
                "catalog/service.go",
                "rows, err := StreamItems(ctx, db, tenantID)",
                [
                    ["defer", "rows.close", "not closed", "closed only on the success path"],
                    ["early return", "client disconnect", "write error", "scan error"],
                    ["connection leak", "pool exhaustion", "maxopenconns", "ten connections", "hangs"],
                ],
                [
                    ["catalog/service.go", "rows, err := StreamItems(ctx, db, tenantID)"],
                    ["catalog/service.go", "if err := writeItem(w, item); err != nil {"],
                    ["catalog/service.go", "rows.Close()"],
                    ["catalog/store.go", "return db.QueryContext(ctx,"],
                ],
            )
        ],
    },
    {
        "case_id": "s-e2c7",
        "split": "sealed",
        "title": "Invoice total batching",
        "language": "Python",
        "context": (
            "Statement runs pass up to 50,000 invoice ids, and the database rejects statements with "
            "more than 65,535 bound parameters. Totals come from the returned rows, never from the "
            "requested id list."
        ),
        "base": {
            "billing/repository.py": source('''
                class InvoiceRepository:
                    def __init__(self, connection):
                        self.connection = connection

                    def by_ids(self, tenant_id: str, invoice_ids: list[str]) -> dict[str, dict]:
                        if not invoice_ids:
                            return {}
                        placeholders = ", ".join(["%s"] * len(invoice_ids))
                        rows = self.connection.fetch_all(
                            "SELECT id, total_cents FROM invoices "
                            f"WHERE tenant_id = %s AND id IN ({placeholders})",
                            (tenant_id, *invoice_ids),
                        )
                        return {row["id"]: row for row in rows}
            '''),
            "billing/service.py": source('''
                from .repository import InvoiceRepository


                def totals(repository: InvoiceRepository, tenant_id: str, invoice_ids: list[str]) -> int:
                    invoices = repository.by_ids(tenant_id, invoice_ids)
                    return sum(invoice["total_cents"] for invoice in invoices.values())
            '''),
        },
        "changed": {
            "billing/repository.py": source('''
                CHUNK = 500


                class InvoiceRepository:
                    def __init__(self, connection):
                        self.connection = connection

                    def by_ids(self, tenant_id: str, invoice_ids: list[str]) -> dict[str, dict]:
                        found: dict[str, dict] = {}
                        for start in range(0, len(invoice_ids), CHUNK):
                            chunk = invoice_ids[start : start + CHUNK]
                            placeholders = ", ".join(["%s"] * len(chunk))
                            rows = self.connection.fetch_all(
                                "SELECT id, total_cents FROM invoices "
                                f"WHERE tenant_id = %s AND id IN ({placeholders})",
                                (tenant_id, *chunk),
                            )
                            found.update({row["id"]: row for row in rows})
                        return found
            '''),
            "billing/service.py": source('''
                from .repository import InvoiceRepository


                def totals(repository: InvoiceRepository, tenant_id: str, invoice_ids: list[str]) -> int:
                    unique_ids = sorted(set(invoice_ids))
                    invoices = repository.by_ids(tenant_id, unique_ids)
                    return sum(invoice["total_cents"] for invoice in invoices.values())
            '''),
        },
        "findings": [],
    },
]


def run_git(repo: Path, *args: str, env: dict | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def write_files(repo: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def line_for(files: dict[str, str], file: str, needle: str) -> int:
    content = files[file]
    if content.count(needle) != 1:
        raise ValueError(f"needle must be unique in {file}: {needle!r}")
    return content[: content.index(needle)].count("\n") + 1


def build_case(case: dict, index: int) -> dict:
    repo = CASES_ROOT / case["split"] / case["case_id"] / "repo"
    repo.mkdir(parents=True)
    run_git(repo, "init", "-q", "--initial-branch=main")
    run_git(repo, "config", "user.name", "Contextual Benchmark")
    run_git(repo, "config", "user.email", "benchmark@example.invalid")

    env = os.environ | {
        "GIT_AUTHOR_NAME": "Contextual Benchmark",
        "GIT_AUTHOR_EMAIL": "benchmark@example.invalid",
        "GIT_COMMITTER_NAME": "Contextual Benchmark",
        "GIT_COMMITTER_EMAIL": "benchmark@example.invalid",
    }

    def commit(files: dict[str, str], message: str, when: str) -> None:
        write_files(repo, files)
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        run_git(repo, "add", "-A")
        run_git(repo, "commit", "-q", "-m", message, env=env)

    # Optional pre-base history, so a reviewer can recover why a guard exists.
    # `HEAD^` stays the base and `HEAD` stays the change under review.
    for step_index, step in enumerate(case.get("history", [])):
        commit(step["files"], step["message"], f"2023-{step_index + 1:02d}-05T00:00:00+0000")

    commit(case["base"], "base", f"2024-01-{index + 1:02d}T00:00:00+0000")
    commit(case["changed"], "change", f"2024-02-{index + 1:02d}T00:00:00+0000")

    expected_commits = len(case.get("history", [])) + 2
    if run_git(repo, "rev-list", "--count", "HEAD") != str(expected_commits):
        raise ValueError(f"{case['case_id']} does not have {expected_commits} commits")
    changed_paths = run_git(repo, "diff", "--name-only", "HEAD^", "HEAD").splitlines()
    if len(changed_paths) < 2:
        raise ValueError(f"{case['case_id']} is not a multi-file change")
    if run_git(repo, "status", "--porcelain"):
        raise ValueError(f"{case['case_id']} is dirty")

    final_files = case["base"] | case["changed"]
    oracle_findings = []
    for number, item in enumerate(case["findings"], 1):
        file, needle = item["location"]
        line = line_for(final_files, file, needle)
        anchors = []
        for anchor_file, anchor_needle in item["anchors"]:
            anchor_line = line_for(final_files, anchor_file, anchor_needle)
            anchors.append({"file": anchor_file, "line_start": anchor_line, "line_end": anchor_line})
        oracle_findings.append(
            {
                "finding_id": f"{case['case_id']}-f{number}",
                "severity": item["severity"],
                "category": item["category"],
                "language": case["language"],
                "file": file,
                "line_start": line,
                "line_end": line,
                "concept_groups": item["concept_groups"],
                "causal_anchors": anchors,
            }
        )
    return {
        "case_id": case["case_id"],
        "split": case["split"],
        "language": case["language"],
        "findings": oracle_findings,
    }


def main() -> int:
    if CASES_ROOT.exists():
        shutil.rmtree(CASES_ROOT)
    CASES_ROOT.mkdir()
    oracle_cases = [build_case(case, index) for index, case in enumerate(CASES)]
    manifest = {
        "format_version": 1,
        "cases": [
            {
                "case_id": case["case_id"],
                "split": case["split"],
                "title": case["title"],
                "context": case["context"],
            }
            | ({"spec": case["spec"]} if case.get("spec") else {})
            for case in CASES
        ],
    }
    (CASES_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (PRIVATE_ROOT / "oracle.json").write_text(
        json.dumps({"format_version": 1, "cases": oracle_cases}, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"cases": len(CASES), "findings": sum(len(c["findings"]) for c in CASES)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
