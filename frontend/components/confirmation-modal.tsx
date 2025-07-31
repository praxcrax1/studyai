"use client"

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { AlertTriangle } from "lucide-react"

interface ConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  description: string
  confirmText?: string
  isDestructive?: boolean
}

export function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirm",
  isDestructive = false,
}: ConfirmationModalProps) {
  const handleConfirm = () => {
    onConfirm()
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 border-white/20 text-white max-w-md backdrop-blur-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-3 text-xl">
            <div className={`rounded-full p-2 ${isDestructive ? "bg-red-500/20" : "bg-blue-500/20"}`}>
              <AlertTriangle className={`h-5 w-5 ${isDestructive ? "text-red-400" : "text-blue-400"}`} />
            </div>
            <span>{title}</span>
          </DialogTitle>
          <DialogDescription className="text-slate-300 text-base mt-2">{description}</DialogDescription>
        </DialogHeader>

        <div className="flex space-x-3 mt-6">
          <Button
            onClick={onClose}
            variant="outline"
            className="flex-1 bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/40 font-medium"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            className={`flex-1 font-medium ${
              isDestructive
                ? "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                : "bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            } text-white`}
          >
            {confirmText}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
