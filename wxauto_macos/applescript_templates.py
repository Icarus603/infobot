"""
AppleScript 模板模組

提供各種微信操作的 AppleScript 模板
"""

from typing import Any, Dict, Optional


class AppleScriptTemplates:
    """AppleScript 模板類"""
    
    @staticmethod
    def activate_wechat() -> str:
        """激活微信應用的 AppleScript"""
        return '''
        tell application "WeChat"
            activate
            delay 1
        end tell
        '''
    
    @staticmethod
    def check_wechat_running() -> str:
        """檢查微信是否運行的 AppleScript"""
        return '''
        tell application "System Events"
            return (name of processes) contains "WeChat"
        end tell
        '''
    
    @staticmethod
    def get_wechat_window_info() -> str:
        """獲取微信窗口信息的 AppleScript"""
        return '''
        tell application "System Events"
            tell process "WeChat"
                if (count of windows) > 0 then
                    tell window 1
                        return {position, size, title}
                    end tell
                else
                    return {}
                end if
            end tell
        end tell
        '''
    
    @staticmethod
    def search_contact(contact_name: str) -> str:
        """搜索聯繫人的 AppleScript"""
        escaped_name = contact_name.replace('"', '\\"')
        return f'''
        tell application "System Events"
            tell process "WeChat"
                try
                    -- 激活微信
                    set frontmost to true
                    delay 1
                    
                    -- 使用 Cmd+F 打開搜索
                    key code 3 using command down  -- Cmd+F
                    delay 1.5
                    
                    -- 清除搜索框
                    key code 0 using command down  -- Cmd+A
                    delay 0.3
                    keystroke "{escaped_name}"
                    delay 2
                    
                    -- 按回車選擇第一個結果
                    key code 36  -- Return
                    delay 1.5
                    
                    -- 按 Escape 關閉搜索框
                    key code 53  -- Escape
                    delay 0.5
                    
                    return true
                on error
                    return false
                end try
            end tell
        end tell
        '''
    
    @staticmethod
    def send_message(message: str) -> str:
        """發送消息的 AppleScript"""
        escaped_message = message.replace('"', '\\"').replace("\\", "\\\\")
        return f'''
        tell application "System Events"
            tell process "WeChat"
                try
                    -- 確保微信處於活動狀態
                    set frontmost to true
                    delay 0.5
                    
                    -- 輸入消息
                    keystroke "{escaped_message}"
                    delay 0.5
                    
                    -- 發送消息 (按回車)
                    key code 36  -- Return
                    delay 0.5
                    
                    return true
                on error
                    return false
                end try
            end tell
        end tell
        '''
    
    @staticmethod
    def send_message_with_clipboard(message: str) -> str:
        """使用剪貼板發送消息的 AppleScript (適用於中文)"""
        escaped_message = message.replace('"', '\\"').replace("\\", "\\\\")
        return f'''
        -- 將消息複製到剪貼板
        set the clipboard to "{escaped_message}"
        
        tell application "System Events"
            tell process "WeChat"
                try
                    -- 確保微信處於活動狀態
                    set frontmost to true
                    delay 0.5
                    
                    -- 貼上消息
                    key code 9 using command down  -- Cmd+V
                    delay 0.5
                    
                    -- 發送消息 (按回車)
                    key code 36  -- Return
                    delay 0.5
                    
                    return true
                on error
                    return false
                end try
            end tell
        end tell
        '''
    
    @staticmethod
    def get_chat_messages() -> str:
        """獲取聊天消息的 AppleScript (實驗性)"""
        return '''
        tell application "System Events"
            tell process "WeChat"
                try
                    if (count of windows) > 0 then
                        tell window 1
                            tell splitter group 1
                                -- 嘗試獲取聊天區域的內容
                                if (count of splitter groups) > 1 then
                                    tell splitter group 2
                                        if (count of scroll areas) > 0 then
                                            tell scroll area 1
                                                -- 獲取所有文本內容
                                                set messageTexts to {}
                                                repeat with messageGroup in groups
                                                    try
                                                        set messageText to value of static text 1 of messageGroup
                                                        set end of messageTexts to messageText
                                                    end try
                                                end repeat
                                                return messageTexts
                                            end tell
                                        end if
                                    end tell
                                end if
                            end tell
                        end tell
                    end if
                    return {}
                on error
                    return {}
                end try
            end tell
        end tell
        '''
    
    @staticmethod
    def get_contact_list() -> str:
        """獲取聯繫人列表的 AppleScript"""
        return '''
        tell application "System Events"
            tell process "WeChat"
                try
                    if (count of windows) > 0 then
                        tell window 1
                            tell splitter group 1
                                if (count of scroll areas) > 0 then
                                    tell scroll area 1
                                        tell table 1
                                            set contactNames to {}
                                            repeat with tableRow in rows
                                                try
                                                    set contactName to value of static text 1 of UI element 1 of tableRow
                                                    set end of contactNames to contactName
                                                end try
                                            end repeat
                                            return contactNames
                                        end tell
                                    end tell
                                end if
                            end tell
                        end tell
                    end if
                    return {}
                on error
                    return {}
                end try
            end tell
        end tell
        '''
    
    @staticmethod
    def take_screenshot(save_path: str) -> str:
        """截圖的 AppleScript"""
        return f'''
        do shell script "screencapture -x '{save_path}'"
        '''
    
    @staticmethod
    def get_wechat_version() -> str:
        """獲取微信版本的 AppleScript"""
        return '''
        tell application "System Events"
            tell process "WeChat"
                try
                    tell (first menu bar item of menu bar 1 whose title is "WeChat")
                        click
                        delay 0.5
                        tell (first menu item of menu 1 whose title contains "About")
                            click
                            delay 1
                        end tell
                    end tell
                    
                    -- 獲取關於窗口中的版本信息
                    if (count of windows) > 0 then
                        tell window "About WeChat"
                            set versionText to value of static text 2
                            key code 53  -- Escape to close
                            return versionText
                        end tell
                    end if
                on error
                    return "未知版本"
                end try
            end tell
        end tell
        ''' 