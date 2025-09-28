document.addEventListener('DOMContentLoaded', function() {
    console.log('🏇 At Yarışı Analizi başlatılıyor...');

    // DOM elementleri
    const citySelect = document.getElementById('citySelect');
    const checkDataBtn = document.getElementById('checkDataBtn');
    const scrapeAndSaveBtn = document.getElementById('scrapeAndSaveBtn');
    const quickCalculateBtn = document.getElementById('quickCalculateBtn');
    const scrapeBtn = document.getElementById('scrapeBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const statusMessage = document.getElementById('statusMessage');
    const resultsContainer = document.getElementById('resultsContainer');
    const summaryStats = document.getElementById('summaryStats');
    const results = document.getElementById('results');

    let currentData = null;

    // Mobil cihaz kontrolü
    function isMobileDevice() {
        return window.innerWidth <= 768 || 
               /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    // Mobil optimizasyonları
    if (isMobileDevice()) {
        // Touch eventi optimizasyonları
        document.body.style.webkitTouchCallout = 'none';
        document.body.style.webkitUserSelect = 'none';
        
        // Mobil scroll optimizasyonu
        document.addEventListener('touchstart', function() {}, {passive: true});
        document.addEventListener('touchmove', function() {}, {passive: true});
    }

    // Ekran yönlendirme değişikliği
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            // Tablo genişliğini yeniden hesapla
            const tables = document.querySelectorAll('.horse-table');
            tables.forEach(table => {
                table.style.width = 'auto';
                setTimeout(() => table.style.width = '100%', 100);
            });
        }, 500);
    });

    // Şehir seçimi değiştiğinde butonları aktif et
    citySelect.addEventListener('change', function() {
        const hasCity = this.value !== '';
        checkDataBtn.disabled = !hasCity;
        scrapeAndSaveBtn.disabled = !hasCity;
        quickCalculateBtn.disabled = !hasCity;
        scrapeBtn.disabled = !hasCity;
        
        // Reset download button and clear results
        downloadBtn.disabled = true;
        currentData = null;
        resultsContainer.style.display = 'none';
        summaryStats.style.display = 'none';
        results.innerHTML = '';
        statusMessage.innerHTML = '';
    });

    // Status mesajı göster
    function showStatus(message, type = 'info') {
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'danger' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        statusMessage.innerHTML = '<div class="alert ' + alertClass + '">' + message + '</div>';
    }

    // Loading göster
    function showLoading(button, text = 'İşleniyor...') {
        button.disabled = true;
        button.innerHTML = '<i class="fa fa-spinner fa-spin"></i> ' + text;
    }

    // Loading'i kapat ve butonu eski haline getir
    function hideLoading(button, originalText) {
        button.disabled = false;
        button.innerHTML = originalText;
    }

    // Kayıtlı veriyi kontrol et
    checkDataBtn.addEventListener('click', async function() {
        const city = citySelect.value;
        if (!city) return;

        const originalText = this.innerHTML;
        showLoading(this, 'Kontrol ediliyor...');

        try {
            const response = await fetch('/api/check_saved_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });

            const data = await response.json();
            
            if (data.success) {
                if (data.has_data) {
                    showStatus('✅ ' + city + ' için kayıtlı veri bulundu. ' + data.file_count + ' dosya mevcut.', 'success');
                    quickCalculateBtn.disabled = false;
                } else {
                    showStatus('⚠️ ' + city + ' için kayıtlı veri bulunamadı. Önce veri çekmelisiniz.', 'warning');
                }
            } else {
                showStatus('❌ Hata: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Veri kontrol hatası:', error);
            showStatus('❌ Veri kontrolünde hata oluştu.', 'danger');
        }

        hideLoading(this, originalText);
    });

    // Veri çek ve kaydet
    scrapeAndSaveBtn.addEventListener('click', async function() {
        const city = citySelect.value;
        if (!city) return;

        const originalText = this.innerHTML;
        showLoading(this, 'Veri çekiliyor...');

        try {
            const response = await fetch('/api/scrape_and_save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });

            const data = await response.json();
            
            if (data.success) {
                showStatus('✅ ' + city + ' verileri başarıyla çekildi ve kaydedildi!', 'success');
                quickCalculateBtn.disabled = false;
            } else {
                showStatus('❌ Hata: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Veri çekme hatası:', error);
            showStatus('❌ Veri çekme işleminde hata oluştu.', 'danger');
        }

        hideLoading(this, originalText);
    });

    // Hızlı analiz (kayıtlı veriden)
    quickCalculateBtn.addEventListener('click', async function() {
        const city = citySelect.value;
        if (!city) return;

        const originalText = this.innerHTML;
        showLoading(this, 'Analiz yapılıyor...');

        try {
            const response = await fetch('/api/calculate_from_saved', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });

            const data = await response.json();
            
            if (data.success && data.races) {
                showStatus('✅ ' + city + ' analizi tamamlandı!', 'success');
                currentData = data;
                showSummaryStats(data);
                showRaceResults(data);
                resultsContainer.style.display = 'block';
                downloadBtn.disabled = false;
            } else {
                showStatus('❌ Hata: ' + (data.message || data.error || 'Analiz sonucu alınamadı'), 'danger');
            }
        } catch (error) {
            console.error('Analiz hatası:', error);
            showStatus('❌ Analiz işleminde hata oluştu.', 'danger');
        }

        hideLoading(this, originalText);
    });

    // Çek ve analiz yap
    scrapeBtn.addEventListener('click', async function() {
        const city = citySelect.value;
        if (!city) return;

        const originalText = this.innerHTML;
        showLoading(this, 'Çekiliyor ve analiz ediliyor...');

        try {
            const response = await fetch('/api/scrape_and_calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });

            const data = await response.json();
            
            if (data.success && data.races) {
                showStatus('✅ ' + city + ' verileri çekildi ve analiz edildi!', 'success');
                currentData = data;
                showSummaryStats(data);
                showRaceResults(data);
                resultsContainer.style.display = 'block';
                downloadBtn.disabled = false;
            } else {
                showStatus('❌ Hata: ' + (data.message || data.error || 'Sonuç alınamadı'), 'danger');
            }
        } catch (error) {
            console.error('Çekme ve analiz hatası:', error);
            showStatus('❌ İşlemde hata oluştu.', 'danger');
        }

        hideLoading(this, originalText);
    });

    // CSV indirme
    downloadBtn.addEventListener('click', function() {
        if (!currentData) return;
        
        try {
            const csv = convertToCSV(currentData);
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', citySelect.value + '_analiz_' + new Date().toISOString().slice(0, 10) + '.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showStatus('📥 CSV dosyası indirildi!', 'success');
        } catch (error) {
            console.error('CSV indirme hatası:', error);
            showStatus('❌ CSV indirme işleminde hata oluştu.', 'danger');
        }
    });

    // Yükleme göstergesi
    function showLoading(show, message = 'İşlem yapılıyor...') {
        if (show) {
            statusMessage.innerHTML = 
                '<div class="alert alert-info">' +
                '<div class="d-flex align-items-center">' +
                '<div class="spinner-border spinner-border-sm me-2" role="status"></div>' +
                '<span>' + message + '</span>' +
                '</div>' +
                '</div>';
        } else {
            statusMessage.innerHTML = '';
        }
    }

    // Özet istatistikler göster
    function showSummaryStats(data) {
        if (!data.summary_stats) {
            summaryStats.style.display = 'none';
            return;
        }

        const stats = data.summary_stats;
        let html = '';
        html += '<div class="col-md-3">';
        html += '<div class="stats-card">';
        html += '<span class="stats-number">' + (stats.total_races || 0) + '</span>';
        html += '<small>Toplam Koşu</small>';
        html += '</div></div>';
        html += '<div class="col-md-3">';
        html += '<div class="stats-card">';
        html += '<span class="stats-number">' + (stats.total_horses || 0) + '</span>';
        html += '<small>Toplam At</small>';
        html += '</div></div>';
        html += '<div class="col-md-3">';
        html += '<div class="stats-card">';
        html += '<span class="stats-number">' + (stats.avg_score ? stats.avg_score.toFixed(2) : '0.00') + '</span>';
        html += '<small>Ortalama Skor</small>';
        html += '</div></div>';
        html += '<div class="col-md-3">';
        html += '<div class="stats-card">';
        html += '<span class="stats-number">' + (stats.top_horses || 0) + '</span>';
        html += '<small>Yüksek Şanslı</small>';
        html += '</div></div>';
        
        summaryStats.innerHTML = html;
        summaryStats.style.display = 'flex';
    }

    // Pist türü mapping
    function getPistType(pistCode) {
        const pistMap = {
            '1': 'Çim',
            '2': 'Kum', 
            '3': 'Sentetik',
            'Çim': 'Çim',
            'Kum': 'Kum',
            'Sentetik': 'Sentetik',
            'çim': 'Çim',
            'kum': 'Kum',
            'sentetik': 'Sentetik'
        };
        return pistMap[pistCode] || pistCode || '-';
    }

    // Koşu sonuçlarını göster
    function showRaceResults(data) {
        console.log('📊 Sonuçlar gösteriliyor...', data);
        
        if (!data.races || data.races.length === 0) {
            results.innerHTML = '<div class="alert alert-warning">Sonuç bulunamadı.</div>';
            return;
        }
        
        let tabsHtml = '<div class="race-tabs-container"><div class="race-tabs">';
        let contentHtml = '<div class="race-content-container">';

        // Her koşu için sekme ve içerik oluştur
        data.races.forEach(function(race, index) {
            const raceNumber = race.race_number || (index + 1);
            const validHorses = race.horses.filter(h => h.score !== null && h.score !== 0);
            
            // Koşu saati hesapla (16:45'ten başlayarak her koşu 30dk sonra)
            const startHour = 16;
            const startMinute = 45;
            const totalMinutes = startMinute + (index * 30);
            const raceHour = startHour + Math.floor(totalMinutes / 60);
            const raceMinute = totalMinutes % 60;
            const raceTime = raceHour + ':' + (raceMinute < 10 ? '0' : '') + raceMinute;
            
            // Sekme
            tabsHtml += '<button class="race-tab ' + (index === 0 ? 'active' : '') + '" onclick="showRaceTab(' + index + ')" id="tab-' + index + '">';
            tabsHtml += raceNumber + '. Koşu ' + raceTime;
            tabsHtml += '</button>';

            // İçerik
            contentHtml += '<div class="race-content-tab ' + (index === 0 ? 'active' : '') + '" id="race-tab-content-' + index + '">';
            contentHtml += '<div class="table-responsive">';
            contentHtml += '<table class="horse-table">';
            contentHtml += '<thead><tr>';
            contentHtml += '<th width="25">N</th>';
            contentHtml += '<th width="50">At No</th>';
            contentHtml += '<th width="120">At İsmi</th>';
            contentHtml += '<th width="50">Çıktı</th>';
            contentHtml += '<th width="60">Mesafe</th>';
            contentHtml += '<th width="50">Pist</th>';
            contentHtml += '<th width="60">Skor</th>';
            contentHtml += '</tr></thead><tbody>';

            // Atları score'a göre sırala (en düşük score en iyi)
            const sortedHorses = race.horses.slice().sort(function(a, b) {
                const scoreA = a.score || 9999;
                const scoreB = b.score || 9999;
                return scoreA - scoreB;
            });

            sortedHorses.forEach(function(horse, horseIndex) {
                const rank = horseIndex + 1;
                const scoreText = horse.score ? horse.score.toFixed(2) : '-';
                const winChance = horse.win_chance || 0;

                contentHtml += '<tr>';
                contentHtml += '<td><strong>' + rank + '</strong></td>';
                contentHtml += '<td><strong>' + (horse.number || '-') + '</strong></td>';
                contentHtml += '<td class="horse-name"><strong>' + (horse.name || 'Bilinmiyor') + '</strong></td>';
                contentHtml += '<td><strong style="color: ' + (horse.score ? '#28a745' : '#dc3545') + '">' + scoreText + '</strong></td>';
                contentHtml += '<td>' + (horse.distance || '-') + '</td>';
                contentHtml += '<td>' + getPistType(horse.surface) + '</td>';
                contentHtml += '<td><strong style="color: ' + (horse.score ? '#007bff' : '#6c757d') + '">' + scoreText + '</strong></td>';
                contentHtml += '</tr>';
            });

            contentHtml += '</tbody></table></div></div>';
        });

        // "Tüm Koşular" sekmesi ekle
        tabsHtml += '<button class="race-tab" onclick="showAllRaces()" id="tab-all">Tüm Koşular</button>';
        
        // Tüm koşular içeriği
        contentHtml += '<div class="race-content-tab" id="race-tab-content-all">';
        contentHtml += '<div class="row all-races-grid">';
        
        data.races.forEach(function(race, index) {
            const raceNumber = race.race_number || (index + 1);
            const validHorses = race.horses.filter(h => h.score !== null && h.score !== 0);
            const topHorse = race.horses.sort(function(a, b) {
                const scoreA = a.score || 9999;
                const scoreB = b.score || 9999;
                return scoreA - scoreB;
            })[0];
            
            const startHour = 16;
            const startMinute = 45;
            const totalMinutes = startMinute + (index * 30);
            const raceHour = startHour + Math.floor(totalMinutes / 60);
            const raceMinute = totalMinutes % 60;
            const raceTime = raceHour + ':' + (raceMinute < 10 ? '0' : '') + raceMinute;
            
            contentHtml += '<div class="col-md-4 col-sm-6 mb-3">';
            contentHtml += '<div class="race-overview-card">';
            contentHtml += '<h6>' + raceNumber + '. Koşu ' + raceTime + '</h6>';
            contentHtml += '<p class="card-text">';
            contentHtml += '<strong>En İyi:</strong> ' + (topHorse ? topHorse.name || 'Veri yok' : 'Veri yok') + '<br>';
            contentHtml += '<strong>Skor:</strong> ' + (topHorse && topHorse.score ? topHorse.score.toFixed(2) : 'Veri yok') + '<br>';
            contentHtml += '<strong>Atlar:</strong> ' + race.horses.length + ' / Geçerli: ' + validHorses.length;
            contentHtml += '</p>';
            contentHtml += '<button class="btn btn-primary btn-sm" onclick="showRaceTab(' + index + ')">Detay Gör</button>';
            contentHtml += '</div></div>';
        });
        
        contentHtml += '</div></div>';

        tabsHtml += '</div></div>';
        contentHtml += '</div>';

        results.innerHTML = tabsHtml + contentHtml;
        
        // Mobil optimizasyonları uygula
        setTimeout(function() {
            addTouchSupport();
            optimizeTableScroll();
        }, 100);
    }

    // Koşu sekmesi göster
    window.showRaceTab = function(raceIndex) {
        // Tüm sekmeleri pasif yap
        document.querySelectorAll('.race-tab').forEach(function(tab) {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.race-content-tab').forEach(function(content) {
            content.classList.remove('active');
        });
        
        // Seçili sekmeyi aktif yap
        document.getElementById('tab-' + raceIndex).classList.add('active');
        document.getElementById('race-tab-content-' + raceIndex).classList.add('active');
    };

    // Tüm koşuları göster
    window.showAllRaces = function() {
        // Tüm sekmeleri pasif yap
        document.querySelectorAll('.race-tab').forEach(function(tab) {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.race-content-tab').forEach(function(content) {
            content.classList.remove('active');
        });
        
        // "Tüm Koşular" sekmesini aktif yap
        document.getElementById('tab-all').classList.add('active');
        document.getElementById('race-tab-content-all').classList.add('active');
    };

    // Mobil için dokunmatik sekme geçişi
    function addTouchSupport() {
        const raceTabsContainer = document.querySelector('.race-tabs');
        if (raceTabsContainer && isMobileDevice()) {
            let startX = 0;
            let currentX = 0;
            let isDragging = false;

            raceTabsContainer.addEventListener('touchstart', function(e) {
                startX = e.touches[0].clientX;
                isDragging = true;
            }, {passive: true});

            raceTabsContainer.addEventListener('touchmove', function(e) {
                if (!isDragging) return;
                currentX = e.touches[0].clientX;
                const diffX = startX - currentX;
                
                // Yatay scroll
                raceTabsContainer.scrollLeft += diffX * 0.5;
                startX = currentX;
            }, {passive: true});

            raceTabsContainer.addEventListener('touchend', function() {
                isDragging = false;
            }, {passive: true});
        }
    }

    // Mobil için tablo scroll optimizasyonu
    function optimizeTableScroll() {
        const tables = document.querySelectorAll('.table-responsive');
        tables.forEach(function(table) {
            if (isMobileDevice()) {
                table.style.overflowX = 'auto';
                table.style.webkitOverflowScrolling = 'touch';
                
                // Scroll ipucu göster
                const scrollHint = document.createElement('div');
                scrollHint.style.cssText = 
                    'position: absolute;' +
                    'top: 5px;' +
                    'right: 5px;' +
                    'background: rgba(0,0,0,0.7);' +
                    'color: white;' +
                    'padding: 2px 6px;' +
                    'border-radius: 3px;' +
                    'font-size: 10px;' +
                    'pointer-events: none;' +
                    'z-index: 10;';
                scrollHint.textContent = '← → Kaydır';
                table.style.position = 'relative';
                table.appendChild(scrollHint);
                
                // 3 saniye sonra gizle
                setTimeout(function() {
                    if (scrollHint.parentNode) {
                        scrollHint.style.opacity = '0';
                        scrollHint.style.transition = 'opacity 0.5s';
                        setTimeout(function() {
                            scrollHint.remove();
                        }, 500);
                    }
                }, 3000);
            }
        });
    }

    // Veri kontrol butonu
    checkDataBtn.addEventListener('click', async function() {
        const city = citySelect.value;
        if (!city) {
            showStatus('❌ Lütfen bir pist seçin!', 'warning');
            return;
        }

        showLoading(true, 'Kaydedilmiş veriler kontrol ediliyor...');

        try {
            const response = await fetch('/api/check_saved_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });

            const data = await response.json();
            
            if (data.success) {
                if (data.has_data) {
                    showStatus('✅ ' + city + ' için kayıtlı veri bulundu. ' + (data.file_count || 'Veri') + ' mevcut.', 'success');
                    quickCalculateBtn.disabled = false;
                } else {
                    showStatus('⚠️ ' + city + ' için kayıtlı veri bulunamadı. Önce veri çekmelisiniz.', 'warning');
                }
            } else {
                showStatus('❌ Hata: ' + (data.message || data.error), 'danger');
            }
        } catch (error) {
            console.error('Veri kontrol hatası:', error);
            showStatus('❌ Veri kontrolünde hata oluştu.', 'danger');
        } finally {
            showLoading(false);
        }
    });

    // Veri çek ve kaydet
    scrapeAndSaveBtn.addEventListener('click', async function() {
        const city = citySelect.value;
        if (!city) {
            showStatus('❌ Lütfen bir pist seçin!', 'warning');
            return;
        }

        showLoading(true, 'Veriler çekiliyor ve kaydediliyor...');

        try {
            const response = await fetch('/api/scrape_and_save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });

            const data = await response.json();
            
            if (data.success) {
                showStatus('✅ ' + city + ' verileri başarıyla çekildi ve kaydedildi!', 'success');
                quickCalculateBtn.disabled = false;
            } else {
                showStatus('❌ Hata: ' + (data.message || data.error), 'danger');
            }
        } catch (error) {
            console.error('Veri çekme hatası:', error);
            showStatus('❌ Veri çekme işleminde hata oluştu.', 'danger');
        } finally {
            showLoading(false);
        }
    });

    // CSV dönüştürme
    function convertToCSV(data) {
        if (!data || !data.races) return '';
        
        let csv = 'Koşu No,At No,At Adı,Mesafe,Pist,Skor\n';
        
        data.races.forEach(function(race, raceIndex) {
            if (!race.horses) return;
            
            race.horses.forEach(function(horse) {
                const score = horse.score != null && !isNaN(horse.score) ? 
                    horse.score.toFixed(2) : '0.00';
                
                csv += (race.race_number || (raceIndex + 1)) + ',';
                csv += '"' + (horse.number || '') + '",';
                csv += '"' + (horse.name || 'Bilinmiyor') + '",';
                csv += '"' + (horse.distance || '') + '",';
                csv += '"' + (horse.surface || '') + '",';
                csv += score + '\n';
            });
        });
        
        return csv;
    }

    // Sayfa yüklendiğinde butonları sıfırla
    checkDataBtn.disabled = true;
    scrapeAndSaveBtn.disabled = true;
    quickCalculateBtn.disabled = true;
    scrapeBtn.disabled = true;
    downloadBtn.disabled = true;
    
    console.log('✅ At Yarışı Analizi hazır!');
});