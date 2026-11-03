import { GoogleSheetsClient } from '@/services/gsheets'

/**
 * DATA SOURCES
 * 
 * This application uses:
 * - Static JSON files for: closets, family, first aid kits, cleaning schedules
 *   (bundled with the app at build time, version-controlled in Git)
 * - Google Sheets for: inventory items, reminders
 *   (read/written directly from browser via Google Sheets API)
 * - No backend API or database needed
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

// ---------------------------------------------------------------------------
// Closets (Static JSON)
// ---------------------------------------------------------------------------
export const getClosets = () => api.get('/closets')
export const getCloset = (id) => api.get(`/closets/${id}`)
export const createCloset = (data) => api.post('/closets', data)
export const updateCloset = (id, data) => api.put(`/closets/${id}`, data)
export const deleteCloset = (id) => api.delete(`/closets/${id}`)

// Shelves (Static JSON)
export const getShelves = (closetId) => api.get('/shelves', { params: { closet_id: closetId } })
export const createShelf = (data) => api.post('/shelves', data)
export const updateShelf = (id, data) => api.put(`/shelves/${id}`, data)
export const deleteShelf = (id) => api.delete(`/shelves/${id}`)

// Baskets (Static JSON)
export const getBaskets = (shelfId) => api.get('/baskets', { params: { shelf_id: shelfId } })
export const createBasket = (data) => api.post('/baskets', data)
export const updateBasket = (id, data) => api.put(`/baskets/${id}`, data)
export const deleteBasket = (id) => api.delete(`/baskets/${id}`)

// ---------------------------------------------------------------------------
// Inventory (Google Sheets via backend)
// ---------------------------------------------------------------------------
export const getBasketInventory = (basketId) => api.get(`/inventory/basket/${basketId}`)
export const upsertInventoryItem = (basketId, itemName, data) =>
  api.put(`/inventory/basket/${basketId}/item/${itemName}`, data)
export const deleteInventoryItem = (id) => api.delete(`/inventory/item/${id}`)
export const scanBasket = (qrToken) => api.get(`/inventory/scan/${qrToken}`)
export const getBasketQrUrl = (basketId) => `/api/inventory/basket/${basketId}/qr.png`

// ---------------------------------------------------------------------------
// Reminders (Google Sheets via backend)
// ---------------------------------------------------------------------------
export const getWashReminders = () => api.get('/reminders/wash')
export const acknowledgeWashReminder = (id) => api.patch(`/reminders/wash/${id}/acknowledge`)
export const getSeasonalReminders = () => api.get('/reminders/seasonal')
export const acknowledgeSeasonalReminder = (id) => api.patch(`/reminders/seasonal/${id}/acknowledge`)

// ---------------------------------------------------------------------------
// Cleaning (Static JSON)
// ---------------------------------------------------------------------------
export const getRooms = () => api.get('/cleaning/rooms')
export const getRoomChecklist = (room, sessionToken) =>
  api.get(`/cleaning/${room}`, { params: sessionToken ? { session_token: sessionToken } : {} })
export const completeItem = (room, itemKey, sessionToken) =>
  api.post(`/cleaning/${room}/complete/${itemKey}`, null, { params: { session_token: sessionToken } })
export const uncompleteItem = (room, itemKey, sessionToken) =>
  api.delete(`/cleaning/${room}/complete/${itemKey}`, { params: { session_token: sessionToken } })
export const resetSession = (room, sessionToken) =>
  api.delete(`/cleaning/${room}/session`, { params: { session_token: sessionToken } })

// ---------------------------------------------------------------------------
// First Aid (Static JSON)
// ---------------------------------------------------------------------------
export const getBasicKit = (category) =>
  api.get('/firstaid/kit/basic', { params: category ? { category } : {} })
export const getAdvancedBins = () => api.get('/firstaid/kit/advanced/bins')
export const getAdvancedKit = (subBin) =>
  api.get('/firstaid/kit/advanced', { params: subBin ? { sub_bin: subBin } : {} })
export const getCprSteps = () => api.get('/firstaid/cpr')

// ---------------------------------------------------------------------------
// Family (Static JSON)
// ---------------------------------------------------------------------------
export const getFamilyMembers = () => api.get('/family')
export const createFamilyMember = (data) => api.post('/family', data)
export const updateFamilyMember = (id, data) => api.put(`/family/${id}`, data)
export const deleteFamilyMember = (id) => api.delete(`/family/${id}`)
