/**
 * Payment API client for manual UPI payment flow.
 */

import { API_BASE } from '../config';
import { getStoredTokens } from './auth';

// ============================================
// TYPES
// ============================================

export interface PaymentRequest {
  id: string;
  user_id: string;
  user_email?: string;
  user_name?: string;
  amount: number;
  upi_transaction_id?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  processed_at?: string;
  processed_by?: string;
  notes?: string;
}

export interface PaymentSubmitResponse {
  success: boolean;
  message: string;
  request_id?: string;
}

export interface PendingStatusResponse {
  has_pending: boolean;
  pending_request?: PaymentRequest;
}

export interface PaymentHistoryResponse {
  success: boolean;
  requests: PaymentRequest[];
  count: number;
}

// ============================================
// HELPERS
// ============================================

function getAuthHeaders(): HeadersInit {
  const { accessToken } = getStoredTokens();
  return {
    'Content-Type': 'application/json',
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Submit a payment request after making UPI payment.
 * @param upiTransactionId - Optional UPI transaction reference
 */
export async function submitPaymentRequest(
  screenshotFile: File,
  upiTransactionId?: string
): Promise<PaymentSubmitResponse> {
  const formData = new FormData();
  formData.append('screenshot', screenshotFile);
  if (upiTransactionId) {
    formData.append('upi_transaction_id', upiTransactionId);
  }

  const { accessToken } = getStoredTokens();
  const headers: HeadersInit = {
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };

  const response = await fetch(`${API_BASE}/payment/request`, {
    method: 'POST',
    headers: headers,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Payment request failed' }));
    throw new Error(error.detail || 'Payment request failed');
  }

  return response.json();
}

/**
 * Check if current user has a pending payment request.
 */
export async function getPaymentStatus(): Promise<PendingStatusResponse> {
  const response = await fetch(`${API_BASE}/payment/status`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get payment status' }));
    throw new Error(error.detail || 'Failed to get payment status');
  }

  return response.json();
}

/**
 * Get payment history for current user.
 */
export async function getPaymentHistory(): Promise<PaymentHistoryResponse> {
  const response = await fetch(`${API_BASE}/payment/history`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get payment history' }));
    throw new Error(error.detail || 'Failed to get payment history');
  }

  return response.json();
}
