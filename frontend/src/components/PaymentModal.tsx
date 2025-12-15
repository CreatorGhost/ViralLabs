/**
 * Payment Modal for manual UPI payment flow.
 * Shows UPI ID, allows user to confirm payment after making UPI transfer.
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Copy,
  Check,
  Loader2,
  Smartphone,
  IndianRupee,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { submitPaymentRequest } from '../api/payment';

// ============================================
// CONFIGURATION - Update these values
// ============================================
const UPI_ID = '7704090366@ybl';
const AMOUNT = 50;
const PLAN_NAME = '10 Credits Pack';
const CREDITS_PER_PACK = 10;

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type ModalState = 'form' | 'loading' | 'success' | 'error';

export default function PaymentModal({ isOpen, onClose, onSuccess }: PaymentModalProps) {
  const [state, setState] = useState<ModalState>('form');
  const [transactionId, setTransactionId] = useState('');
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCopyUPI = async () => {
    try {
      await navigator.clipboard.writeText(UPI_ID);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = UPI_ID;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSubmit = async () => {
    if (!screenshot) {
      setError('Please upload a screenshot of the payment.');
      return;
    }
    setState('loading');
    setError(null);

    try {
      await submitPaymentRequest(screenshot, transactionId || undefined);
      setState('success');
      onSuccess?.();
    } catch (err) {
      setState('error');
      setError(err instanceof Error ? err.message : 'Something went wrong');
    }
  };

  const handleClose = () => {
    if (state === 'loading') return; // Don't close while loading
    setState('form');
    setTransactionId('');
    setScreenshot(null);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div
              className="relative w-full max-w-md bg-[#0B0C10] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-white/10">
                <h2 className="text-xl font-semibold">Complete Your Payment</h2>
                <button
                  onClick={handleClose}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                  disabled={state === 'loading'}
                >
                  <X className="w-5 h-5 text-white/60" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6">
                {state === 'form' && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-6"
                  >
                    {/* Plan Info */}
                    <div className="p-4 rounded-xl bg-violet-500/10 border border-violet-500/20">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-white/90 font-medium">{PLAN_NAME}</span>
                          <p className="text-xs text-white/50 mt-0.5">10 script + 10 thumbnail generations</p>
                        </div>
                        <div className="flex items-center gap-1 text-xl font-bold">
                          <IndianRupee className="w-5 h-5" />
                          {AMOUNT.toLocaleString('en-IN')}
                        </div>
                      </div>
                    </div>

                    {/* UPI Instructions */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-sm text-white/60">
                        <Smartphone className="w-4 h-4" />
                        <span>Pay using PhonePe, GPay, or any UPI app</span>
                      </div>

                      {/* UPI ID */}
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                        <p className="text-xs text-white/50 mb-2">UPI ID</p>
                        <div className="flex items-center justify-between gap-3">
                          <code className="text-lg font-mono text-violet-400">{UPI_ID}</code>
                          <button
                            onClick={handleCopyUPI}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 transition-colors text-sm"
                          >
                            {copied ? (
                              <>
                                <Check className="w-4 h-4 text-emerald-400" />
                                <span className="text-emerald-400">Copied!</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-4 h-4" />
                                <span>Copy</span>
                              </>
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Amount */}
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                        <p className="text-xs text-white/50 mb-2">Amount to Pay</p>
                        <div className="flex items-center gap-1 text-2xl font-bold text-white">
                          <IndianRupee className="w-6 h-6" />
                          {AMOUNT.toLocaleString('en-IN')}
                        </div>
                      </div>
                    </div>

                    {/* Transaction ID (Optional) */}
                    <div>
                      <label className="block text-sm text-white/60 mb-2">
                        Transaction ID (Optional)
                      </label>
                      <input
                        type="text"
                        value={transactionId}
                        onChange={(e) => setTransactionId(e.target.value)}
                        placeholder="Enter UPI transaction reference"
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50 transition-colors"
                      />
                      <p className="mt-2 text-xs text-white/40">
                        This helps us verify your payment faster
                      </p>
                    </div>

                    {/* Screenshot Upload */}
                    <div>
                      <label className="block text-sm text-white/60 mb-2">
                        Payment Screenshot
                      </label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => setScreenshot(e.target.files ? e.target.files[0] : null)}
                        className="w-full text-sm text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
                      />
                       <p className="mt-2 text-xs text-white/40">
                        This is mandatory for payment verification.
                      </p>
                    </div>

                    {/* Submit Button */}
                    <button
                      onClick={handleSubmit}
                      disabled={!screenshot}
                      className="w-full py-3.5 rounded-xl bg-violet-600 hover:bg-violet-500 font-medium transition-colors flex items-center justify-center gap-2 disabled:bg-gray-500"
                    >
                      <CheckCircle2 className="w-5 h-5" />
                      I've Completed the Payment
                    </button>

                    <p className="text-center text-xs text-white/40">
                      Click above only after you have successfully transferred the amount
                    </p>
                  </motion.div>
                )}

                {state === 'loading' && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-12"
                  >
                    <Loader2 className="w-12 h-12 text-violet-500 animate-spin mb-4" />
                    <p className="text-white/60">Submitting your payment request...</p>
                  </motion.div>
                )}

                {state === 'success' && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center justify-center py-8 text-center"
                  >
                    <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6">
                      <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Payment Request Submitted!</h3>
                    <p className="text-white/60 mb-6 max-w-sm">
                      Thank you! Your {CREDITS_PER_PACK} credits will be added within 24 hours after we verify your payment. We'll notify you via email.
                    </p>
                    <button
                      onClick={handleClose}
                      className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 font-medium transition-colors"
                    >
                      Got it
                    </button>
                  </motion.div>
                )}

                {state === 'error' && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center justify-center py-8 text-center"
                  >
                    <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mb-6">
                      <AlertCircle className="w-8 h-8 text-red-400" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Something went wrong</h3>
                    <p className="text-white/60 mb-6 max-w-sm">
                      {error || 'Failed to submit payment request. Please try again.'}
                    </p>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setState('form')}
                        className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 font-medium transition-colors"
                      >
                        Try Again
                      </button>
                      <button
                        onClick={handleClose}
                        className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 font-medium transition-colors"
                      >
                        Close
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
