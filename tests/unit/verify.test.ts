import { describe, expect, it } from 'vitest';
import { parseScope, pickPython } from '../../scripts/verify.mjs';

describe('parseScope', () => {
  it('reads "--scope <value>"', () => {
    expect(parseScope(['--scope', 'lesson:x'])).toEqual({ scope: 'lesson:x', ignored: [] });
  });

  it('reads "--scope=<value>"', () => {
    expect(parseScope(['--scope=lesson:x'])).toEqual({ scope: 'lesson:x', ignored: [] });
  });

  it('returns null scope when there are no arguments', () => {
    expect(parseScope([])).toEqual({ scope: null, ignored: [] });
  });

  it('collects unknown arguments as ignored', () => {
    expect(parseScope(['--fast', '--scope', 'day:1', 'extra'])).toEqual({
      scope: 'day:1',
      ignored: ['--fast', 'extra'],
    });
  });

  it('treats "--scope" without a value as ignored', () => {
    expect(parseScope(['--scope'])).toEqual({ scope: null, ignored: ['--scope'] });
  });
});

describe('pickPython', () => {
  const runner = (ok: string[]) => {
    const calls: string[] = [];
    const run = (cmd: string, args: string[]) => {
      calls.push(`${cmd} ${args.join(' ')}`);
      return ok.includes(cmd);
    };
    return { run, calls };
  };

  it('prefers python3 when it works', () => {
    const { run, calls } = runner(['python3', 'python']);
    expect(pickPython(run)).toBe('python3');
    expect(calls).toEqual(['python3 --version']);
  });

  it('falls back to python when python3 fails', () => {
    const { run, calls } = runner(['python']);
    expect(pickPython(run)).toBe('python');
    expect(calls).toEqual(['python3 --version', 'python --version']);
  });

  it('returns null when neither works', () => {
    const { run } = runner([]);
    expect(pickPython(run)).toBeNull();
  });
});
