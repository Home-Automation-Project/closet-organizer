/**
 * Google Sheets Integration for Browser
 * 
 * This module provides direct browser-based access to Google Sheets
 * for reading and writing inventory and reminders data.
 * 
 * Setup required:
 * 1. Create Google Cloud project
 * 2. Enable Google Sheets API
 * 3. Create OAuth 2.0 credentials (public/web type)
 * 4. Add credentials to environment (see .env.example)
 * 5. Create Sheets for inventory and reminders
 * 6. Share sheets with your Google account
 */

// Load Google API library dynamically
const loadGoogleAPI = () => {
  return new Promise((resolve, reject) => {
    if (window.gapi) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = 'https://apis.google.com/js/api.js'
    script.onload = () => {
      window.gapi.load('client:auth2', () => {
        resolve()
      })
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

export class GoogleSheetsClient {
  constructor(config) {
    this.clientId = config.clientId
    this.apiKey = config.apiKey
    this.inventorySheetId = config.inventorySheetId
    this.remindersSheetId = config.remindersSheetId
    this.scopes = 'https://www.googleapis.com/auth/spreadsheets'
    this.isInitialized = false
    this.isAuthenticated = false
  }

  /**
   * Initialize the Google API client
   */
  async initialize() {
    if (this.isInitialized) return

    try {
      await loadGoogleAPI()

      await window.gapi.client.init({
        apiKey: this.apiKey,
        clientId: this.clientId,
        scope: this.scopes,
        discoveryDocs: ['https://sheets.googleapis.com/$discovery/rest?version=v4'],
      })

      this.isInitialized = true
      console.log('Google API initialized')

      // Check if already authenticated
      const auth = window.gapi.auth2.getAuthInstance()
      if (auth && auth.isSignedIn.get()) {
        this.isAuthenticated = true
      }
    } catch (error) {
      console.error('Failed to initialize Google API:', error)
      throw error
    }
  }

  /**
   * Authenticate user with Google OAuth
   */
  async authenticate() {
    try {
      await this.initialize()
      const auth = window.gapi.auth2.getAuthInstance()

      if (!auth.isSignedIn.get()) {
        await auth.signIn()
      }

      this.isAuthenticated = true
      console.log('User authenticated with Google')
      return true
    } catch (error) {
      console.error('Authentication failed:', error)
      throw error
    }
  }

  /**
   * Sign out user
   */
  async signOut() {
    try {
      const auth = window.gapi.auth2.getAuthInstance()
      await auth.signOut()
      this.isAuthenticated = false
      console.log('User signed out')
    } catch (error) {
      console.error('Sign out failed:', error)
      throw error
    }
  }

  /**
   * Get current user info
   */
  getCurrentUser() {
    const auth = window.gapi.auth2.getAuthInstance()
    if (auth && auth.isSignedIn.get()) {
      const profile = auth.currentUser.get().getBasicProfile()
      return {
        id: profile.getId(),
        name: profile.getName(),
        email: profile.getEmail(),
        image: profile.getImageUrl(),
      }
    }
    return null
  }

  /**
   * Read data from a Google Sheet
   * @param {string} sheetId - The Sheet ID
   * @param {string} range - The range to read (e.g., "Sheet1!A1:D10")
   */
  async readSheet(sheetId, range) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated. Call authenticate() first.')
    }

    try {
      const response = await window.gapi.client.sheets.spreadsheets.values.get({
        spreadsheetId: sheetId,
        range: range,
      })

      return response.result.values || []
    } catch (error) {
      console.error(`Failed to read sheet ${sheetId}:`, error)
      throw error
    }
  }

  /**
   * Write data to a Google Sheet
   * @param {string} sheetId - The Sheet ID
   * @param {string} range - The range to write (e.g., "Sheet1!A1:D10")
   * @param {Array} values - 2D array of values to write
   */
  async writeSheet(sheetId, range, values) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated. Call authenticate() first.')
    }

    try {
      const response = await window.gapi.client.sheets.spreadsheets.values.update({
        spreadsheetId: sheetId,
        range: range,
        valueInputOption: 'USER_ENTERED',
        resource: {
          values: values,
        },
      })

      return response.result
    } catch (error) {
      console.error(`Failed to write to sheet ${sheetId}:`, error)
      throw error
    }
  }

  /**
   * Append data to a Google Sheet
   * @param {string} sheetId - The Sheet ID
   * @param {string} range - The range to append to (e.g., "Sheet1!A:D")
   * @param {Array} values - 2D array of values to append
   */
  async appendSheet(sheetId, range, values) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated. Call authenticate() first.')
    }

    try {
      const response = await window.gapi.client.sheets.spreadsheets.values.append({
        spreadsheetId: sheetId,
        range: range,
        valueInputOption: 'USER_ENTERED',
        resource: {
          values: values,
        },
      })

      return response.result
    } catch (error) {
      console.error(`Failed to append to sheet ${sheetId}:`, error)
      throw error
    }
  }

  /**
   * Get inventory items from Google Sheets
   * 
   * Expected structure:
   * | Basket ID | Item Name | Quantity | Expiration Date | Notes |
   * |-----------|-----------|----------|-----------------|-------|
   * | basket_1  | Sheets    | 10       | 2025-06-01      | 1000 ct |
   */
  async getInventory(basketId = null) {
    try {
      const rows = await this.readSheet(this.inventorySheetId, 'Inventory!A2:E1000')

      const items = rows.map((row) => ({
        basketId: row[0] || '',
        itemName: row[1] || '',
        quantity: parseInt(row[2]) || 0,
        expirationDate: row[3] || null,
        notes: row[4] || '',
      }))

      // Filter by basketId if specified
      if (basketId) {
        return items.filter((item) => item.basketId === basketId)
      }

      return items
    } catch (error) {
      console.error('Failed to get inventory:', error)
      throw error
    }
  }

  /**
   * Update or add an inventory item
   */
  async updateInventoryItem(basketId, itemName, quantity, expirationDate = null, notes = '') {
    try {
      const rows = await this.readSheet(this.inventorySheetId, 'Inventory!A2:E1000')

      // Find existing item
      let rowIndex = -1
      for (let i = 0; i < rows.length; i++) {
        if (rows[i][0] === basketId && rows[i][1] === itemName) {
          rowIndex = i
          break
        }
      }

      if (rowIndex >= 0) {
        // Update existing item
        const range = `Inventory!A${rowIndex + 2}:E${rowIndex + 2}`
        await this.writeSheet(this.inventorySheetId, range, [
          [basketId, itemName, quantity, expirationDate || '', notes],
        ])
      } else {
        // Add new item
        await this.appendSheet(this.inventorySheetId, 'Inventory!A:E', [
          [basketId, itemName, quantity, expirationDate || '', notes],
        ])
      }

      return {
        basketId,
        itemName,
        quantity,
        expirationDate,
        notes,
      }
    } catch (error) {
      console.error('Failed to update inventory item:', error)
      throw error
    }
  }

  /**
   * Delete an inventory item
   */
  async deleteInventoryItem(basketId, itemName) {
    try {
      const rows = await this.readSheet(this.inventorySheetId, 'Inventory!A2:E1000')

      // Find and remove item
      const newRows = rows.filter((row) => !(row[0] === basketId && row[1] === itemName))

      // Clear and rewrite the sheet
      await this.writeSheet(this.inventorySheetId, 'Inventory!A2:E1000', newRows)

      return true
    } catch (error) {
      console.error('Failed to delete inventory item:', error)
      throw error
    }
  }

  /**
   * Get reminders from Google Sheets
   * 
   * Expected structure:
   * | ID | Category | Text | Due Date | Acknowledged |
   * |----|----------|------|----------|--------------|
   * | 1  | WASH     | Wash sheets | 2025-06-01 | |
   */
  async getReminders() {
    try {
      const rows = await this.readSheet(this.remindersSheetId, 'Reminders!A2:E1000')

      const reminders = rows
        .filter((row) => row[0]) // Skip empty rows
        .map((row) => ({
          id: row[0] || '',
          category: row[1] || '',
          text: row[2] || '',
          dueDate: row[3] || null,
          acknowledged: row[4] ? true : false,
          acknowledgedAt: row[4] || null,
        }))

      return reminders
    } catch (error) {
      console.error('Failed to get reminders:', error)
      throw error
    }
  }

  /**
   * Create a new reminder
   */
  async createReminder(category, text, dueDate = null) {
    try {
      const id = `reminder_${Date.now()}`
      await this.appendSheet(this.remindersSheetId, 'Reminders!A:E', [[id, category, text, dueDate || '', '']])

      return {
        id,
        category,
        text,
        dueDate,
        acknowledged: false,
      }
    } catch (error) {
      console.error('Failed to create reminder:', error)
      throw error
    }
  }

  /**
   * Acknowledge a reminder
   */
  async acknowledgeReminder(reminderId) {
    try {
      const rows = await this.readSheet(this.remindersSheetId, 'Reminders!A2:E1000')

      let rowIndex = -1
      for (let i = 0; i < rows.length; i++) {
        if (rows[i][0] === reminderId) {
          rowIndex = i
          break
        }
      }

      if (rowIndex >= 0) {
        const row = rows[rowIndex]
        const acknowledgedAt = new Date().toISOString()
        const range = `Reminders!A${rowIndex + 2}:E${rowIndex + 2}`
        await this.writeSheet(this.remindersSheetId, range, [[row[0], row[1], row[2], row[3], acknowledgedAt]])

        return {
          id: reminderId,
          acknowledged: true,
          acknowledgedAt,
        }
      }

      throw new Error(`Reminder ${reminderId} not found`)
    } catch (error) {
      console.error('Failed to acknowledge reminder:', error)
      throw error
    }
  }
}
