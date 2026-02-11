// Simple markdown-like text formatter for chat messages
export const formatMarkdown = (text) => {
  if (!text) return ''
  
  // Replace **bold** with <strong>
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // Replace *italic* with <em>
  text = text.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  // Replace `code` with <code>
  text = text.replace(/`(.+?)`/g, '<code class="bg-gray-200 px-1 rounded">$1</code>')
  
  // Replace links [text](url) with <a>
  text = text.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline">$1</a>')
  
  // Replace line breaks
  text = text.replace(/\n/g, '<br>')
  
  return text
}

export const MarkdownText = ({ text, className = '' }) => {
  const formattedText = formatMarkdown(text)
  
  return (
    <div 
      className={className}
      dangerouslySetInnerHTML={{ __html: formattedText }}
    />
  )
}
