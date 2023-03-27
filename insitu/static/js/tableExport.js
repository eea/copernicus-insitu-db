/*The MIT License (MIT)
Copyright (c) 2014 https://github.com/kayalshri/
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.*/

function s2ab(s) {
    let buf = new ArrayBuffer(s.length);
    let view = new Uint8Array(buf);
    for (let i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
    return buf;
  }

(function($){
    $.fn.extend({
        tableExport: function(options) {
            var defaults = {
                    separator: ',',
                    ignoreColumn: [],
                    tableName:'Sheet1',
                    type:'csv',
                    pdfFontSize:14,
                    pdfLeftMargin:20,
                    escape:'true',
                    htmlContent:'false',
                    consoleLog:'false',
                    filename: 'File.xls',
            };
            
            var options = $.extend(defaults, options);
            let el = this;
            
            if(defaults.type == 'csv' || defaults.type == 'txt'){
            
                // Header
                let tdData ="";
                $(el).find('thead').find('tr').each(function() {
                tdData += "\n";					
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                tdData += '"' + parseString($(this)) + '"' + defaults.separator;								
                            }
                        }
                        
                    });
                    tdData = $.trim(tdData);
                    tdData = $.trim(tdData).substring(0, tdData.length -1);
                });
                
                // Row vs Column
                $(el).find('tbody').find('tr').each(function() {
                tdData += "\n";
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                tdData += '"'+ parseString($(this)) + '"'+ defaults.separator;
                            }
                        }
                    });
                    //tdData = $.trim(tdData);
                    tdData = $.trim(tdData).substring(0, tdData.length -1);
                });
                
                //output
                if(defaults.consoleLog == 'true'){
                    console.log(tdData);
                }
                var base64data = "base64," + $.base64.encode(tdData);
                window.open('data:application/'+defaults.type+';filename=exportData;' + base64data);
            }else if(defaults.type == 'sql'){
            
                // Header
                let tdData ="INSERT INTO `"+defaults.tableName+"` (";
                $(el).find('thead').find('tr').each(function() {
                
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                tdData += '`' + parseString($(this)) + '`,' ;							
                            }
                        }
                        
                    });
                    tdData = $.trim(tdData);
                    tdData = $.trim(tdData).substring(0, tdData.length -1);
                });
                tdData += ") VALUES ";
                // Row vs Column
                $(el).find('tbody').find('tr').each(function() {
                tdData += "(";
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                tdData += '"'+ parseString($(this)) + '",';
                            }
                        }
                    });
                    
                    tdData = $.trim(tdData).substring(0, tdData.length -1);
                    tdData += "),";
                });
                tdData = $.trim(tdData).substring(0, tdData.length -1);
                tdData += ";";
                
                //output
                //console.log(tdData);
                
                if(defaults.consoleLog == 'true'){
                    console.log(tdData);
                }
                
                var base64data = "base64," + $.base64.encode(tdData);
                window.open('data:application/sql;filename=exportData;' + base64data);
                
            
            }else if(defaults.type == 'json'){
            
                var jsonHeaderArray = [];
                $(el).find('thead').find('tr').each(function() {
                    var tdData ="";	
                    var jsonArrayTd = [];
                
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                jsonArrayTd.push(parseString($(this)));						
                            }
                        }
                    });									
                    jsonHeaderArray.push(jsonArrayTd);						
                    
                });
                
                var jsonArray = [];
                $(el).find('tbody').find('tr').each(function() {
                    var tdData ="";	
                    var jsonArrayTd = [];
                
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                jsonArrayTd.push(parseString($(this)));							
                            }
                        }
                    });									
                    jsonArray.push(jsonArrayTd);									
                    
                });
                
                var jsonExportArray =[];
                jsonExportArray.push({header:jsonHeaderArray,_data:jsonArray});
                
                //Return as JSON
                //console.log(JSON.stringify(jsonExportArray));
                
                //Return as Array
                //console.log(jsonExportArray);
                if(defaults.consoleLog == 'true'){
                    console.log(JSON.stringify(jsonExportArray));
                }
                var base64data = "base64," + $.base64.encode(JSON.stringify(jsonExportArray));
                window.open('data:application/json;filename=exportData;' + base64data);
            }else if(defaults.type == 'xml'){
            
                let xml = '<?xml version="1.0" encoding="utf-8"?>';
                xml += '<tabledata><fields>';

                // Header
                $(el).find('thead').find('tr').each(function() {
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){					
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                xml += "<field>" + parseString($(this)) + "</field>";
                            }
                        }
                    });									
                });					
                xml += '</fields><data>';
                
                // Row Vs Column
                let rowCount=1;
                $(el).find('tbody').find('tr').each(function() {
                    xml += '<row id="'+rowCount+'">';
                    let colCount=0;
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){	
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                xml += "<column-"+colCount+">"+parseString($(this))+"</column-"+colCount+">";
                            }
                        }
                        colCount++;
                    });															
                    rowCount++;
                    xml += '</row>';
                });					
                xml += '</data></tabledata>'
                
                if(defaults.consoleLog == 'true'){
                    console.log(xml);
                }
                
                var base64data = "base64," + $.base64.encode(xml);
                window.open('data:application/xml;filename=exportData;' + base64data);

            }else if(defaults.type == 'excel' || defaults.type == 'doc'|| defaults.type == 'powerpoint'  ){
                //console.log($(this).html());
                let excel="<table>";
                // Header
                $(el).find('thead').find('tr').each(function() {
                    excel += "<tr>";
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){					
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                let colSpan = ($(this).prop('colSpan') > 0) ? $(this).prop('colSpan') : 1;
								let rowSpan = ($(this).prop('rowSpan') > 0) ? $(this).prop('rowSpan') : 1;
								excel += "<td colSpan='"+colSpan+"' rowSpan='"+rowSpan+"'>" + parseString($(this))+ "</td>";
                            }
                        }
                    });	
                    excel += '</tr>';						
                    
                });					
                
                
                // Row Vs Column
                let rowCount=1;
                $(el).find('tbody').find('tr').each(function() {
                    excel += "<tr>";
                    let colCount=0;
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){	
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                let colSpan = ($(this).prop('colSpan') > 0) ? $(this).prop('colSpan') : 1;
								let rowSpan = ($(this).prop('rowSpan') > 0) ? $(this).prop('rowSpan') : 1;
								excel += "<td colSpan='"+colSpan+"' rowSpan='"+rowSpan+"'>" + parseString($(this))+ "</td>";
                            }
                        }
                        colCount++;
                    });															
                    rowCount++;
                    excel += '</tr>';
                });					
                excel += '</table>'
                
                if(defaults.consoleLog == 'true'){
                    console.log(excel);
                }
                
                let excelFile = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:x='urn:schemas-microsoft-com:office:"+defaults.type+"' xmlns='http://www.w3.org/TR/REC-html40'>";
                excelFile += "<head>";
                excelFile += "<!--[if gte mso 9]>";
                excelFile += "<xml>";
                excelFile += "<x:ExcelWorkbook>";
                excelFile += "<x:ExcelWorksheets>";
                excelFile += "<x:ExcelWorksheet>";
                excelFile += "<x:Name>";
                excelFile += "{worksheet}";
                excelFile += "</x:Name>";
                excelFile += "<x:WorksheetOptions>";
                excelFile += "<x:DisplayGridlines/>";
                excelFile += "</x:WorksheetOptions>";
                excelFile += "</x:ExcelWorksheet>";
                excelFile += "</x:ExcelWorksheets>";
                excelFile += "</x:ExcelWorkbook>";
                excelFile += "</xml>";
                excelFile += "<![endif]-->";
                excelFile += "</head>";
                excelFile += "<body>";
                excelFile += excel;
                excelFile += "</body>";
                excelFile += "</html>";

                var base64data = "base64," + $.base64.encode(excelFile);
                let blob=new Blob([s2ab(excelFile)], {type:'data:application/vnd.ms-'+defaults.type});
                if (navigator.msSaveOrOpenBlob) {
                    navigator.msSaveOrOpenBlob(blob, defaults.filename);
                }
                else {
                  let link=document.createElement('a');
                  link.href=window.URL.createObjectURL(blob);
                  link.download=defaults.filename;
                  document.body.appendChild(link);
                  link.click();
                  link.remove();
                }
            }else if(defaults.type == 'png'){
                html2canvas($(el), {
                    onrendered: function(canvas) {										
                        let img = canvas.toDataURL("image/png");
                        window.open(img);
                        
                        
                    }
                });		
            }else if(defaults.type == 'pdf'){

                let doc = new jsPDF('p','pt', 'a4', true);
                doc.setFontSize(defaults.pdfFontSize);
                
                // Header
                let startColPosition=defaults.pdfLeftMargin;
                $(el).find('thead').find('tr').each(function() {
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){					
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                let colPosition = startColPosition+ (index * 50);
                                doc.text(colPosition,20, parseString($(this)));
                            }
                        }
                    });									
                });					
            
            
                // Row Vs Column
                let startRowPosition = 20; let page =1;let rowPosition=0;
                $(el).find('tbody').find('tr').each(function(index,_data) {
                   let rowCalc = index+1;
                    
                if (rowCalc % 26 == 0){
                    doc.addPage();
                    page++;
                    startRowPosition=startRowPosition+10;
                }
                rowPosition=(startRowPosition + (rowCalc * 10)) - ((page -1) * 280);
                    
                    $(this).filter(':visible').find('th').each(function(index,_data) {
                        if ($(this).css('display') != 'none'){	
                            if(defaults.ignoreColumn.indexOf(index) == -1){
                                let colPosition = startColPosition+ (index * 50);
                                doc.text(colPosition,rowPosition, parseString($(this)));
                            }
                        }
                        
                    });															
                    
                });					
                                    
                // Output as Data URI
                doc.output('datauri');

            }
            
            
            function parseString(data){
                let content_data
                if(defaults.htmlContent == 'true'){
                    content_data = data.html().trim();
                }else{
                    content_data = data.text().trim();
                }
                
                if(defaults.escape == 'true'){
                    content_data = escape(content_data);
                }
                
                
                
                return content_data;
            }
        
        }
    });
})(jQuery);
