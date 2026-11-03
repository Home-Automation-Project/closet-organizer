import { GoogleSheetsClient } from '@/services/gsheets'

/**
 * DATA SOURCES
 * 
 * This application is completely static and uses:
 * - Static JSON files for: closets, family, first aid kits, cleaning schedules
 *   (bundled with the app at build time, version-controlled in Git)
 * - Google Sheets API for: inventory items, reminders
 *   (read/written directly from browser via Google Sheets API)
 * - No backend API or database needed
 * - No backend server required
 */

// Initialize Google Sheets client (configured from environment)
let gsheets = null

export function initializeGoogleSheets() {
  const config = {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
    apiKey: import.meta.env.VITE_GOOGLE_API_KEY || '',
    inventorySheetId: import.meta.env.VITE_INVENTORY_SHEET_ID || '',
    remindersSheetId: import.meta.env.VITE_REMINDERS_SHEET_ID || '',
  }

  // Only initialize if credentials are provided
  if (!config.clientId || !config.apiKey) {
    console.warn('Google Sheets not configured. Inventory and reminders will not work.')
    return false
  }

  gsheets = new GoogleSheetsClient(config)
  return true
}

export function getGoogleSheetsClient() {
  return gsheets
}

/**
 * Load JSON data from bundled files
 */
async function loadJSON(path) {
  try {
    const response = await fetch(path)
    if (!response.ok) throw new Error(`Failed to load ${path}`)
    return await response.json()
  } catch (error) {
    console.error(`Error loading ${path}:`, error)
    throw error
  }
}

/**
 * Cached JSON data
 */
let closetsData = null
let familyData = null
let firstaidData = null
let cleaningData = null

/**
 * STATIC DATA LOADERS (from JSON files)
 */

export async function getClosets() {
  if (!closetsData) {
    closetsData = await loadJSON('/data/closets.json')
  }
  return closetsData.closets || []
}

export async function getCloset(closetId) {
  const closets = await getClosets()
  return closets.find((c) => c.id === closetId)
}

export async function getShelves(closetId) {
  const closet = await getCloset(closetId)
  return closet ? closet.shelves || [] : []
}

export async function getBaskets(shelfId) {
  // Find the shelf across all closets
  const closets = await getClosets()
  for (const closet of closets) {
    const shelf = closet.shelves?.find((s) => s.id === shelfId)
    if (shelf) return shelf.baskets || []
  }
  return []
}

/**
 * FAMILY (Static JSON)
 */

export async function getFamilyMembers() {
  if (!familyData) {
    familyData = await loadJSON('/data/family.json')
  }
  return familyData.members || []
}

export async function getFamilyMember(memberId) {
  const members = await getFamilyMembers()
  return members.find((m) => m.id === memberId)
}

export async function createFamilyMember(data) {
  console.warn('Family data is static. To add family members, edit data/family.json and commit to Git.')
  throw new Error('Family data is read-only. Edit data/family.json to make changes.')
}

export async function updateFamilyMember(memberId, data) {
  console.warn('Family data is static. To update family members, edit data/family.json and commit to Git.')
  throw new Error('Family data is read-only. Edit data/family.json to make changes.')
}

export async function deleteFamilyMember(memberId) {
  console.warn('Family data is static. To delete family members, edit data/family.json and commit to Git.')
  throw new Error('Family data is read-only. Edit data/family.json to make changes.')
}

/**
 * FIRST AID (Static JSON)
 */

export async function getFirstaidData() {
  if (!firstaidData) {
    firstaidData = await loadJSON('/data/firstaid.json')
  }
  return firstaidData
}

export async function getBasicKit() {
  const data = await getFirstaidData()
  return data.basicKit || {}
}

export async function getBasicKitItems(category = null) {
  const data = await getFirstaidData()
  const items = data.basicKit?.items || []
  if (category) {
    return items.filter((item) => item.category === category)
  }
  return items
}

export async function getAdvancedBins() {
  const data = await getFirstaidData()
  return data.advancedKit?.bins || []
}

export async function getAdvancedKit() {
  const data = await getFirstaidData()
  return data.advancedKit || {}
}

export async function getAdvancedKitItems(binLabel = null) {
  const data = await getFirstaidData()
  const items = data.advancedKit?.items || []
  if (binLabel) {
    return items.filter((item) => item.bin === binLabel)
  }
  return items
}

export async function getCprSteps() {
  const data = await getFirstaidData()
  return data.cpr || {}
}

/**
 * CLEANING (Static JSON)
 */

export async function getCleaningData() {
  if (!cleaningData) {
    cleaningData = await loadJSON('/data/cleaning.json')
  }
  return cleaningData
}

export async function getRooms() {
  const data = await getCleaningData()
  return data.rooms || []
}

export async function getRoom(roomId) {
  const rooms = await getRooms()
  return rooms.find((r) => r.id === roomId)
}

/**
 * INVENTORY (Google Sheets via browser)
 */

export async function getBasketInventory(basketId) {
  if (!gsheets || !gsheets.isAuthenticated) {
    console.warn('Google Sheets not authenticated. Inventory not available.')
    return []
  }

  try {
    return await gsheets.getInventory(basketId)
  } catch (error) {
    console.error('Failed to get inventory:', error)
    return []
  }
}

export async function updateInventoryItem(basketId, itemName, quantity, expirationDate = null, notes = '') {
  if (!gsheets || !gsheets.isAuthenticated) {
    throw new Error('Google Sheets not authenticated. Please log in first.')
  }

  return await gsheets.updateInventoryItem(basketId, itemName, quantity, expirationDate, notes)
}

export async function deleteInventoryItem(basketId, itemName) {
  if (!gsheets || !gsheets.isAuthenticated) {
    throw new Error('Google Sheets not authenticated. Please log in first.')
  }

  return await gsheets.deleteInventoryItem(basketId, itemName)
}

/**
 * REMINDERS (Google Sheets via browser)
 */

export async function getReminders() {
  if (!gsheets || !gsheets.isAuthenticated) {
    console.warn('Google Sheets not authenticated. Reminders not available.')
    return []
  }

  try {
    return await gsheets.getReminders()
  } catch (error) {
    console.error('Failed to get reminders:', error)
    return []
  }
}

export async function createReminder(category, text, dueDate = null) {
  if (!gsheets || !gsheets.isAuthenticated) {
    throw new Error('Google Sheets not authenticated. Please log in first.')
  }

  return await gsheets.createReminder(category, text, dueDate)
}

export async function acknowledgeReminder(reminderId) {
  if (!gsheets || !gsheets.isAuthenticated) {
    throw new Error('Google Sheets not authenticated. Please log in first.')
  }

  return await gsheets.acknowledgeReminder(reminderId)
}

/**
 * AUTHENTICATION (Google Account)
 */

export async function authenticateGoogle() {
  if (!gsheets) {
    console.error('Google Sheets not initialized')
    return false
  }

  try {
    return await gsheets.authenticate()
  } catch (error) {
    console.error('Google authentication failed:', error)
    throw error
  }
}

export async function signOutGoogle() {
  if (!gsheets) {
    return
  }

  try {
    await gsheets.signOut()
  } catch (error) {
    console.error('Google sign out failed:', error)
  }
}

export function getCurrentGoogleUser() {
  if (!gsheets) {
    return null
  }

  return gsheets.getCurrentUser()
}

export function isGoogleAuthenticated() {
  return gsheets && gsheets.isAuthenticated
}
