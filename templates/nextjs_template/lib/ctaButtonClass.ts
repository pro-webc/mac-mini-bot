/**
 * design_spec: primary #eceff4 / primary_foreground #111827 / border #334155
 */
const base =
  "inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[14px] px-6 py-3 text-base font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4] motion-safe:transition-colors";

const enabledClasses =
  "bg-[#eceff4] text-[#111827] hover:bg-[#d8dce6] active:bg-[#c5cbd6]";

const disabledClasses =
  "cursor-not-allowed border border-[#334155] bg-[#1f2937] text-[#94a3b8]";

export function ctaButtonClass(disabledBtn?: boolean): string {
  return `${base} ${disabledBtn ? disabledClasses : enabledClasses}`;
}

const outlineBase =
  "inline-flex min-h-[48px] min-w-[44px] items-center justify-center gap-2 rounded-[14px] border border-[#334155] bg-transparent px-6 py-3 text-base font-semibold text-[#eceff4] transition-colors hover:border-[#eceff4] hover:bg-[#1f2937] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#eceff4] motion-safe:transition-colors";

export function secondaryOutlineClass(): string {
  return outlineBase;
}
