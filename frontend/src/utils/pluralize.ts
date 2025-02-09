// export const pluralize = (count: number, forms: string = "s"): string => {
//     if (count === 1) return forms.split(",")[0] || "";
//     const parts = forms.split(",");

//     if (count === 0 && parts.length === 3) {
//       return parts[2];
//     }

//     return parts.length > 1 ? parts[1] : parts[0];
//   };

export const pluralize = (count?: number, forms = 's'): string => {
  if (!count) return '' // If count is 0 or undefined, return an empty string

  const parts = forms.split(',')

  // If only one form is provided (e.g., "s"), return "s" for plural cases
  if (parts.length === 1) {
    return count === 1 ? '' : parts[0]
  }

  // General rule: Singular -> first form, Plural -> second form
  return count === 1 ? parts[0] : parts[1]
}
