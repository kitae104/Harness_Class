import { describe, expect, it } from 'vitest';
import { planWasi, wasiPackageSpec } from '../../scripts/ensure_astro_wasi.mjs';

describe('wasiPackageSpec', () => {
  it('pins the WASI package to the installed native binding version', () => {
    expect(wasiPackageSpec('0.4.1')).toBe('@astrojs/compiler-binding-wasm32-wasi@0.4.1');
  });

  it('rejects a missing version', () => {
    expect(() => wasiPackageSpec(undefined)).toThrow();
  });
});

describe('planWasi', () => {
  it('always installs the fallback on Windows (Smart App Control blocks the native binding intermittently)', () => {
    expect(planWasi({ platform: 'win32', nativeLoads: true, wasiInstalled: false })).toBe('install');
  });

  it('keeps an installed fallback as is', () => {
    expect(planWasi({ platform: 'win32', nativeLoads: false, wasiInstalled: true })).toBe('wasi-present');
  });

  it('does nothing on Linux/macOS when the native binding loads (CI, Vercel)', () => {
    expect(planWasi({ platform: 'linux', nativeLoads: true, wasiInstalled: false })).toBe('native');
    expect(planWasi({ platform: 'darwin', nativeLoads: true, wasiInstalled: false })).toBe('native');
  });

  it('installs the fallback anywhere the native binding fails to load', () => {
    expect(planWasi({ platform: 'linux', nativeLoads: false, wasiInstalled: false })).toBe('install');
  });
});
