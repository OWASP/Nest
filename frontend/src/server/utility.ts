export type IndexedObject = {
  [key: string]: unknown
}

export const removeIdxPrefix = (obj: IndexedObject): IndexedObject => {
  const newObj: IndexedObject = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = key.startsWith('idx_') ? key.slice(4) : key
      newObj[newKey] = obj[key]
    }
  }
  return newObj
}
