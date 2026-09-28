import React, { act, useState } from 'react';
import { createRoot, Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, jest } from '@jest/globals';
import { Modal } from '@/components/ui/Modal';

let root: Root;
let host: HTMLDivElement;

beforeEach(() => {
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
});

afterEach(() => {
  act(() => root.unmount());
  host.remove();
});

describe('Modal keyboard accessibility', () => {
  it('moves focus into the dialog and restores it to the trigger when closed', async () => {
    function Harness() {
      const [open, setOpen] = useState(false);
      return (
        <>
          <button type="button" onClick={() => setOpen(true)}>Open dialog</button>
          <Modal isOpen={open} onClose={() => setOpen(false)} title="Update stock">
            <button type="button">Save changes</button>
          </Modal>
        </>
      );
    }

    await act(async () => root.render(<Harness />));
    const trigger = host.querySelector('button')!;
    act(() => trigger.focus());
    act(() => trigger.click());
    await act(async () => new Promise((resolve) => setTimeout(resolve, 0)));
    const close = host.querySelector('[aria-label="Close dialog"]')!;
    expect(document.activeElement).toBe(close);

    act(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })));
    expect(document.activeElement).toBe(trigger);
    expect(host.querySelector('[role="dialog"]')).toBeNull();
  });

  it('wraps forward keyboard focus from the final control to the first', async () => {
    await act(async () => root.render(
      <Modal isOpen onClose={jest.fn()} title="Update stock">
        <button type="button">Save changes</button>
      </Modal>,
    ));
    await act(async () => new Promise((resolve) => setTimeout(resolve, 0)));
    const close = host.querySelector('[aria-label="Close dialog"]')!;
    const save = Array.from(host.querySelectorAll('button')).find((button) => button.textContent === 'Save changes')!;
    act(() => save.focus());
    act(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true })));
    expect(document.activeElement).toBe(close);
  });
});
