// 我真诚地保证：
// 我自己独立地完成了整个程序从分析、设计到编码的所有工作。
// 如果在上述过程中，我遇到了什么困难而求教于人，那么，我将在程序实习报告中
// 详细地列举我所遇到的问题，以及别人给我的提示。
// 我的程序里中凡是引用到其他程序或文档之处，
// 例如教材、课堂笔记、网上的源代码以及其他参考书上的代码段,
// 我都已经在程序的注释里很清楚地注明了引用的出处。
// 我从未抄袭过别人的程序，也没有盗用别人的程序。
// 安俊豪
package v1

import "github.com/gogf/gf/v2/frame/g"

// ProfileReq 获取个人信息请求
type ProfileReq struct {
	g.Meta `path:"/user/profile" method:"get" tags:"用户服务" summary:"获取个人信息"`
}

// ProfileRes 获取个人信息响应
type ProfileRes struct {
	Id        uint64 `json:"id" dc:"用户ID"`
	Name      string `json:"name" dc:"用户姓名"`
	Email     string `json:"email" dc:"邮箱"`
	Phone     string `json:"phone" dc:"手机号"`
	Status    int8   `json:"status" dc:"状态"`
	CreatedAt string `json:"created_at" dc:"创建时间"`
}
