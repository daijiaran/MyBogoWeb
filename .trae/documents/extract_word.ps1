$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\数据库原理作业选择.docx')
$text = $doc.Content.Text
$text | Out-File -FilePath 'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt' -Encoding UTF8
$doc.Close()
$word.Quit()
Get-Content 'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt'
