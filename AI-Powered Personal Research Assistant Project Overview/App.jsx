import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Upload, Send, FileText, MessageCircle, Trash2, BookOpen, Sparkles } from 'lucide-react'
import './App.css'

const API_BASE_URL = 'http://localhost:5000/api'

function App() {
  const [documents, setDocuments] = useState([])
  const [messages, setMessages] = useState([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [isChatting, setIsChatting] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`)
      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents || [])
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    }
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    setSelectedFile(file)
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_BASE_URL}/upload-document`, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setSelectedFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        fetchDocuments()
        
        // Add success message to chat
        setMessages(prev => [...prev, {
          type: 'system',
          content: `Document "${data.filename}" uploaded successfully! ${data.chunks_created} chunks created.`,
          timestamp: new Date().toISOString()
        }])
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Upload failed')
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Upload failed: ${error.message}`,
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsUploading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return

    const userMessage = {
      type: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentMessage('')
    setIsChatting(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: currentMessage
        }),
      })

      if (response.ok) {
        const data = await response.json()
        
        const assistantMessage = {
          type: 'assistant',
          content: data.answer,
          citations: data.citations || [],
          timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, assistantMessage])
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Chat request failed')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsChatting(false)
    }
  }

  const handleDeleteDocument = async (documentId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/delete-document/${documentId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        fetchDocuments()
        setMessages(prev => [...prev, {
          type: 'system',
          content: 'Document deleted successfully.',
          timestamp: new Date().toISOString()
        }])
      }
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              AI Research Assistant
            </h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your documents and chat with your knowledge base. Get AI-powered answers with citations.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document Upload & Management */}
          <div className="lg:col-span-1">
            <Card className="h-fit">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Document Library
                </CardTitle>
                <CardDescription>
                  Upload and manage your documents
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* File Upload */}
                <div className="space-y-3">
                  <Input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleFileSelect}
                    className="cursor-pointer"
                  />
                  <Button 
                    onClick={handleFileUpload}
                    disabled={!selectedFile || isUploading}
                    className="w-full"
                  >
                    {isUploading ? (
                      <>
                        <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Upload Document
                      </>
                    )}
                  </Button>
                </div>

                <Separator />

                {/* Document List */}
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-muted-foreground">
                    Uploaded Documents ({documents.length})
                  </h4>
                  <ScrollArea className="h-64">
                    {documents.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No documents uploaded yet</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {documents.map((doc) => (
                          <div key={doc.document_id} className="flex items-center justify-between p-3 border rounded-lg bg-muted/50">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium truncate">{doc.filename}</p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(doc.upload_date).toLocaleDateString()}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteDocument(doc.document_id)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="h-[600px] flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="h-5 w-5" />
                  Chat with Your Documents
                </CardTitle>
                <CardDescription>
                  Ask questions about your uploaded documents
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                {/* Messages */}
                <ScrollArea className="flex-1 pr-4">
                  <div className="space-y-4">
                    {messages.length === 0 ? (
                      <div className="text-center py-12 text-muted-foreground">
                        <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p className="text-lg font-medium mb-2">Ready to help!</p>
                        <p className="text-sm">Upload some documents and start asking questions.</p>
                      </div>
                    ) : (
                      messages.map((message, index) => (
                        <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-[80%] rounded-lg p-4 ${
                            message.type === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : message.type === 'error'
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : message.type === 'system'
                              ? 'bg-green-100 text-green-800 border border-green-200'
                              : 'bg-muted'
                          }`}>
                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            
                            {/* Citations */}
                            {message.citations && message.citations.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-gray-200">
                                <p className="text-xs font-medium mb-2 opacity-75">Sources:</p>
                                <div className="space-y-2">
                                  {message.citations.map((citation, citIndex) => (
                                    <div key={citIndex} className="text-xs bg-white/20 rounded p-2">
                                      <div className="flex items-center gap-2 mb-1">
                                        <Badge variant="secondary" className="text-xs">
                                          [{citIndex + 1}]
                                        </Badge>
                                        <span className="font-medium">{citation.filename}</span>
                                      </div>
                                      <p className="opacity-75">{citation.text}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            <p className="text-xs opacity-50 mt-2">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                    {isChatting && (
                      <div className="flex justify-start">
                        <div className="bg-muted rounded-lg p-4">
                          <div className="flex items-center gap-2">
                            <Sparkles className="h-4 w-4 animate-spin" />
                            <span className="text-sm">Thinking...</span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Message Input */}
                <div className="flex gap-2 mt-4">
                  <Textarea
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about your documents..."
                    className="flex-1 min-h-[60px] resize-none"
                    disabled={isChatting || documents.length === 0}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!currentMessage.trim() || isChatting || documents.length === 0}
                    size="lg"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                
                {documents.length === 0 && (
                  <p className="text-xs text-muted-foreground mt-2 text-center">
                    Upload documents to start chatting
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

