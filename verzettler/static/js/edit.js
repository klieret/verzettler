const addScript = (path, callback) => {
  const scriptElement = document.createElement('script')
  scriptElement.src = path
  scriptElement.async = true
  document.head.appendChild(scriptElement)
  scriptElement.onload = () => {
    callback()
  }
}

const addStyle = (url) => {
  const styleElement = document.createElement('link')
  styleElement.rel = 'stylesheet'
  styleElement.type = 'text/css'
  styleElement.href = url
  document.getElementsByTagName('head')[0].appendChild(styleElement)
}

addStyle('https://cdn.jsdelivr.net/npm/vditor@3.5.5/dist/index.css')
document.addEventListener('DOMContentLoaded', function () {
  var hm = document.createElement('script')
  var s = document.getElementsByTagName('script')[0]
  s.parentNode.insertBefore(hm, s)
  if (document.getElementById('vdit')) {
    addScript('https://cdn.jsdelivr.net/npm/vditor@3.5.5/dist/index.min.js',
      () => {
          vditorScript()
      })
  }
})

