"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Send, Bot, User, Search, Loader2, History } from "lucide-react"
import { ConfirmationModal } from "@/components/confirmation-modal"
import { MarkdownRenderer } from "@/components/markdown-renderer"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  toolCalls?: ToolCall[]
  timestamp?: Date
}

interface ToolCall {
  tool: string
  input: any
}

interface ChatHistoryItem {
  _id: string
  SessionId: string
  History: string
}

interface ChatInterfaceProps {
  token: string
  selectedDocuments: string[]
  onClearChat: () => void
}

export function ChatInterface({ token, selectedDocuments, onClearChat }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [showClearConfirm, setShowClearConfirm] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch chat history on component mount
  useEffect(() => {
    fetchChatHistory()
  }, [token])

  const fetchChatHistory = async () => {
    setIsLoadingHistory(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/all`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const chatHistory: ChatHistoryItem[] = await response.json()
        const parsedMessages = parseChatHistory(chatHistory)
        setMessages(parsedMessages)
      }
    } catch (error) {
      console.error("Failed to fetch chat history:", error)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const parseChatHistory = (chatHistory: ChatHistoryItem[]): Message[] => {
    const messages: Message[] = []

    // Group by SessionId and sort by _id to maintain order
    const groupedBySession: { [key: string]: ChatHistoryItem[] } = {}

    chatHistory.forEach((item) => {
      if (!groupedBySession[item.SessionId]) {
        groupedBySession[item.SessionId] = []
      }
      groupedBySession[item.SessionId].push(item)
    })

    // Process each session
    Object.values(groupedBySession).forEach((sessionItems) => {
      // Sort by _id to maintain chronological order
      sessionItems.sort((a, b) => a._id.localeCompare(b._id))

      sessionItems.forEach((item) => {
        try {
          const historyData = JSON.parse(item.History)
          const messageData = historyData.data || historyData

          const message: Message = {
            id: item._id,
            type: historyData.type === "human" ? "user" : "assistant",
            content: messageData.content || "",
            timestamp: new Date(),
          }

          // Add tool calls if they exist
          if (messageData.tool_calls && messageData.tool_calls.length > 0) {
            message.toolCalls = messageData.tool_calls
          }

          messages.push(message)
        } catch (error) {
          console.error("Failed to parse chat history item:", error)
        }
      })
    })

    return messages
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const requestBody: any = {
        query: input.trim(),
      }

      if (selectedDocuments.length > 0) {
        requestBody.doc_ids = selectedDocuments
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/query`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "assistant",
          content: data.response.answer,
          toolCalls: data.response.tool_calls || [],
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        throw new Error("Failed to get response")
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "Sorry, I encountered an error while processing your request. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClearChat = () => {
    setMessages([])
    onClearChat()
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  return (
    <div className="flex-1 flex flex-col bg-slate-900 overflow-hidden">

      {/* Messages - Scrollable */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {isLoadingHistory ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full p-6 mb-6">
                <Loader2 className="h-16 w-16 text-blue-400 animate-spin" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Loading your chat history...</h3>
              <p className="text-slate-400">Please wait while we fetch your previous conversations</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full p-6 mb-6">
                <Bot className="h-16 w-16 text-blue-400" />
              </div>
              <h3 className="text-2xl font-semibold text-white mb-3">Ready to help you learn</h3>
              <p className="text-slate-400 max-w-md mb-6">
                Upload documents and ask questions to get intelligent answers with source references.
              </p>
              {selectedDocuments.length === 0 && (
                <div className="bg-amber-500/20 border border-amber-500/50 rounded-lg p-4 max-w-md">
                  <p className="text-amber-300 text-sm">
                    💡 Select documents from the sidebar to get more focused answers
                  </p>
                </div>
              )}
            </div>
          ) : (
            <>
              {/* Chat History Header */}
              <div className="flex items-center justify-center mb-6">
                <div className="flex items-center space-x-2 bg-slate-800/50 rounded-full px-4 py-2 border border-slate-700/50">
                  <History className="h-4 w-4 text-slate-400" />
                  <span className="text-slate-400 text-sm">Chat History Loaded</span>
                </div>
              </div>

              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`flex items-start space-x-4 max-w-3xl ${message.type === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
                  >
                    <div
                      className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                        message.type === "user"
                          ? "bg-gradient-to-br from-blue-500 to-purple-600"
                          : "bg-gradient-to-br from-slate-700 to-slate-600"
                      }`}
                    >
                      {message.type === "user" ? (
                        <User className="h-5 w-5 text-white" />
                      ) : (
                        <Bot className="h-5 w-5 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <Card
                        className={`${
                          message.type === "user"
                            ? "bg-gradient-to-br from-blue-600 to-purple-600 border-blue-500/50"
                            : "bg-slate-800/90 border-slate-700/50 backdrop-blur-sm"
                        } shadow-lg`}
                      >
                        <CardContent className="p-5">
                          {message.type === "user" ? (
                            <p className="text-white whitespace-pre-wrap leading-relaxed">{message.content}</p>
                          ) : (
                            <MarkdownRenderer content={message.content} />
                          )}

                          {/* Tool Calls Display */}
                          {message.toolCalls && message.toolCalls.length > 0 && (
                            <div className="mt-6 space-y-4">
                              <div className="flex items-center space-x-2">
                                <div className="h-px bg-slate-600 flex-1"></div>
                                <p className="text-slate-300 text-sm font-medium px-3">Tool Calls</p>
                                <div className="h-px bg-slate-600 flex-1"></div>
                              </div>
                              {message.toolCalls.map((toolCall, index) => (
                                <div
                                  key={index}
                                  className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/50 backdrop-blur-sm"
                                >
                                  <div className="flex items-center space-x-3 mb-3">
                                    <div className="bg-blue-500/20 rounded-full p-2">
                                      <Search className="h-4 w-4 text-blue-400" />
                                    </div>
                                    <Badge
                                      variant="secondary"
                                      className="bg-slate-600/50 text-slate-200 text-xs font-mono px-3 py-1"
                                    >
                                      {toolCall.tool}
                                    </Badge>
                                  </div>
                                  <pre className="text-slate-300 text-xs overflow-x-auto bg-slate-800/50 rounded-lg p-4 border border-slate-600/30">
                                    {JSON.stringify(toolCall.input, null, 2)}
                                  </pre>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Timestamp */}
                          {message.timestamp && (
                            <div
                              className={`mt-3 text-xs ${message.type === "user" ? "text-blue-200" : "text-slate-500"}`}
                            >
                              {formatTimestamp(message.timestamp)}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-4 max-w-3xl">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-600 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <Card className="bg-slate-800 border-slate-700 shadow-lg">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                      <p className="text-slate-300">Thinking...</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <ConfirmationModal
        isOpen={showClearConfirm}
        onClose={() => setShowClearConfirm(false)}
        onConfirm={handleClearChat}
        title="Clear Chat History"
        description="This will permanently delete all messages in this conversation. This action cannot be undone."
        confirmText="Clear Chat"
        isDestructive={true}
      />

      {/* Input - Fixed */}
      <div className="border-t border-slate-700 p-6 flex-shrink-0 bg-slate-800/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents..."
              disabled={isLoading}
              className="flex-1 bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-blue-400 h-12"
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 h-12 px-6"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
